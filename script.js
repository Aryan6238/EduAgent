document.getElementById('run-pipeline').addEventListener('click', runPipeline);

async function runPipeline() {
    const grade = document.getElementById('grade').value;
    const topic = document.getElementById('topic').value;

    // Reset UI
    const pipeline = document.getElementById('pipeline-visualization');
    const finalOutputSection = document.getElementById('final-output');
    pipeline.classList.remove('hidden');
    finalOutputSection.classList.add('hidden');

    // Reset individual steps
    resetStep(1, 'Generating content...');
    resetStep(2, 'Waiting...');
    document.getElementById('step-3').classList.add('hidden');
    document.getElementById('arrow-2').classList.add('hidden');

    try {
        const response = await fetch('http://localhost:8000/generate-assessment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grade: parseInt(grade), topic: topic })
        });

        if (!response.ok) throw new Error('Failed to run pipeline');

        const data = await response.json();
        renderPipeline(data);
    } catch (error) {
        alert('Error connecting to backend. Make sure the FastAPI server is running.');
        console.error(error);
    }
}

function resetStep(num, statusText) {
    const status = document.getElementById(`step-${num}-status`);
    const content = document.getElementById(`step-${num}-content`);
    status.innerText = statusText;
    status.className = 'status-badge processing';
    content.innerHTML = '';
}

function renderPipeline(data) {
    const steps = data.steps;

    // Step 1: Generator
    setActiveStep(1);
    setTimeout(() => {
        updateStep(1, steps[0].output, 'Completed', 'pass');

        // Step 2: Reviewer
        setActiveStep(2);
        setTimeout(() => {
            const reviewStatus = steps[1].output.status;
            updateStep(2, steps[1].output, reviewStatus.toUpperCase(), reviewStatus);

            if (data.refined) {
                // Step 3: Refined Generator
                document.getElementById('step-3').classList.remove('hidden');
                document.getElementById('arrow-2').classList.remove('hidden');
                setActiveStep(3);

                setTimeout(() => {
                    updateStep(3, steps[2].output, 'Completed', 'pass');
                    showFinal(data.final_content);
                }, 1500); // Artificial delay for effect
            } else {
                showFinal(data.final_content);
            }
        }, 1500); // Artificial delay for effect
    }, 1000); // Artificial delay for effect
}

function setActiveStep(num) {
    // Remove active class from all
    for (let i = 1; i <= 3; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) step.classList.remove('active-step');
    }
    // Add to current
    const current = document.getElementById(`step-${num}`);
    if (current) {
        current.classList.add('active-step');
        current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function updateStep(num, output, statusText, statusClass) {
    const status = document.getElementById(`step-${num}-status`);
    const content = document.getElementById(`step-${num}-content`);

    status.innerText = statusText;
    status.className = `status-badge ${statusClass}`;

    let html = '';

    if (output.feedback) {
        html += '<div class="formatted-view"><strong>Reviewer Feedback:</strong><br>' +
            output.feedback.map(f => `<div class="feedback-item">• ${f}</div>`).join('') + '</div>';
    } else if (output.explanation) {
        html += `<div class="formatted-view"><p>${output.explanation}</p>`;
        if (output.mcqs && output.mcqs.length > 0) {
            html += '<strong>Generated MCQs:</strong><br>' +
                output.mcqs.map(m => `
                    <div class="mcq-item">
                        Q: ${m.question}<br>
                        <small>Correct Answer: ${m.answer}</small>
                    </div>
                `).join('') + '</div>';
        }
    }

    // Agent Transparency: Show the actual structured data passed between agents
    html += `
        <div class="json-view">
            <details>
                <summary style="cursor: pointer; font-size: 0.75rem; font-weight: bold; color: var(--accent-color);">[VIEW STRUCTURED AGENT OUTPUT]</summary>
                <pre>${JSON.stringify(output, null, 2)}</pre>
            </details>
        </div>
    `;

    content.innerHTML = html;
}

function showFinal(content) {
    const finalSection = document.getElementById('final-output');
    const display = document.getElementById('final-content-display');

    finalSection.classList.remove('hidden');
    display.innerHTML = `
        <div class="explanation-final">
            <h3 style="color: var(--success);">Final Verified Assessment Content</h3>
            <p>${content.explanation}</p>
        </div>
        <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 20px 0;">
        <div class="mcqs-final">
            <h4>Assessment Items</h4>
            ${content.mcqs.map((m, i) => `
                <div class="mcq-item" style="margin-bottom: 15px;">
                    <strong>Q${i + 1}:</strong> ${m.question}
                    <ul style="list-style: none; padding-left: 15px; margin-top: 8px;">
                        ${m.options.map(o => `<li style="margin-bottom: 4px;">• ${o}</li>`).join('')}
                    </ul>
                    <div style="background: #f1f5f9; padding: 4px 8px; font-size: 0.8rem; border-radius: 4px; display: inline-block;">
                        <strong>Key:</strong> ${m.answer}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    finalSection.scrollIntoView({ behavior: 'smooth' });
}
