<script>
    import axios from 'axios';

    let promptText = "";
    let dagName = "";  // Variable to store the DAG name
    let pyodide;
    let pyodideLoaded = false;
    let errorMessage = '';
    let code = '';
    let isLoading = false;
    let syntaxCheckResult = ''; 
    let showSyntaxCheckResult = false;

    async function loadPyodide() {
        try {
            if (!window.loadPyodide) {
                throw new Error('Pyodide script not loaded');
            }
            pyodide = await window.loadPyodide();
            await pyodide.loadPackage('micropip'); 
            pyodideLoaded = true;
        } catch (error) {
            console.error('Error loading Pyodide:', error);
            errorMessage = 'Failed to load Pyodide.';
        }
    }

    function syncScroll(event) {
        const textarea = event.target;
        const lineNumbers = document.querySelector('.line-numbers');
        lineNumbers.scrollTop = textarea.scrollTop;
    }

    async function submitSchedule() {
        if (!dagName || /\s/.test(dagName)) {
            errorMessage = 'DAG name is required and must be a single string without spaces.';
            return;
        }

        // Append DAG name to the prompt
        const modifiedPromptText = `${promptText}\nPlease name the DAG with this: ${dagName}`;

        const payload = {
            "prompt": modifiedPromptText
        };

        console.log("Modified Payload JSON:", payload);
        isLoading = true;

        try {
            const response = await axios.post('http://127.0.0.1:45000/generate_dag', payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('Response Data:', response.data);
            code = response.data.code;

            code = code.replace(/```python/g, '').replace(/```/g, '').trim();

            if (pyodideLoaded) {
                errorMessage = 'Prompt submitted successfully.';
            } else {
                errorMessage = 'Pyodide is not loaded yet';
            }
        } catch (error) {
            console.error('Error:', error.message || error);
            errorMessage = 'Error occurred: ' + (error.message || error);
        } finally {
            isLoading = false;
        }
    }

    async function checkSyntax() {
        if (pyodideLoaded) {
            try {
                const checkCode = `
import ast

def check_syntax(code):
    try:
        ast.parse(code)
        return "No syntax errors found"
    except SyntaxError as e:
        return f"Syntax error in your code: {e}"

result = check_syntax('''${code}''')
result
                `;
                const result = await pyodide.runPythonAsync(checkCode);
                syntaxCheckResult = result;
                showSyntaxCheckResult = true;
                console.log('Syntax Check Result:', result);
            } catch (error) {
                syntaxCheckResult = 'Error in Python code: ' + error.message;
                showSyntaxCheckResult = true;
                console.error('Error in Python code:', error);
            }
        } else {
            syntaxCheckResult = 'Pyodide is not loaded yet';
            showSyntaxCheckResult = true;
        }
    }

    async function submitDAG() {
        if (!dagName || /\s/.test(dagName)) {
            alert('DAG name is required and must be a single string without spaces.');
            return;
        }

        const payload = {
            dag_name: dagName,
            code: code
        };

        try {
            const response = await axios.post('http://127.0.0.1:45000/upload_code', payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 200) {
                alert("DAG submitted successfully!");
            } else {
                alert("Failed to submit DAG.");
            }
        } catch (error) {
            console.error("Error:", error.message || error);
            alert("Error occurred while submitting DAG: " + (error.message || error));
        }
    }

    import { onMount } from 'svelte';

    onMount(async () => {
        await loadPyodide();
    });
</script>

<svelte:head>
    <script async src="https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"></script>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" />
</svelte:head>

<div class="container">
    <div class="schedule-form">
        <label class="prompt-label">
            Prompt:
            <input type="text" bind:value={promptText} placeholder="Enter your prompt" />
        </label>
        <label class="dag-label">
            DAG Name:
            <input type="text" bind:value={dagName} placeholder="Enter DAG name" />
        </label>
        <button class="submit-button" on:click={submitSchedule} disabled={isLoading || !dagName || /\s/.test(dagName)}>
            {#if isLoading}
                <span class="spinner"></span>
            {/if}
            Send
        </button>
    </div>

    {#if pyodideLoaded}
        <div class="code-editor-container">
            <div class="code-editor">
                <div class="line-numbers">
                    {#each Array(code.split('\n').length) as _, i}
                        <span>{i + 1}</span>
                    {/each}
                </div>
                <textarea bind:value={code} rows="15" placeholder="Your code here..." on:scroll="{syncScroll}" />
            </div>
            <button class="syntax-check-button" on:click={checkSyntax}>Test Code</button>
            <button class="submit-dag-button" on:click={submitDAG}>Submit DAG</button>
        </div>
    {:else if errorMessage}
        <p>{errorMessage}</p>
    {:else}
        <p>Loading Pyodide...</p>
    {/if}

    {#if showSyntaxCheckResult}
        <div class="syntax-check-result">
            <h4>Syntax Check Result:</h4>
            <p>{syntaxCheckResult}</p>
        </div>
    {/if}
</div>

<style>
    .container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 800px;
    margin: auto;
}

.schedule-form {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.prompt-label {
    flex: 1;
    display: flex;
    font-family: 'Poppins', sans-serif;
    flex-direction: column;
    gap: 0.5rem;
}

.prompt-label input {
    width: 95%;
    padding: 0.5rem;
    font-family: 'Poppins', sans-serif;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.dag-label {
    flex: 1;
    display: flex;
    font-family: 'Poppins', sans-serif;
    flex-direction: column;
    gap: 0.5rem;
}

.dag-label input {
    width: 95%;
    padding: 0.5rem;
    font-family: 'Poppins', sans-serif;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}


.submit-button {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    font-family: 'Poppins', sans-serif;
    white-space: nowrap;
    margin-top: 30px;
}

.submit-button:hover {
    background-color: #0056b3;
}

.submit-button:disabled {
    background-color: #007bff;
    opacity: 0.6;
    cursor: not-allowed;
}

.code-editor-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    position: relative;
}

.code-editor {
    position: relative;
    display: flex;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    background-color: #1e1e1e;
    width: 100%;
    max-width: 800px;
}

.line-numbers {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 60px;
    background-color: #2d2d2d;
    color: #888;
    padding: 10px;
    text-align: right;
    font-family: monospace;
    font-size: 16px;
    border-right: 1px solid #444;
    box-sizing: border-box;
    line-height: 1.5em;
    overflow: hidden;
}

.line-numbers span {
    display: block;
    margin: 0 0 0px;
}

textarea {
    flex: 1;
    background-color: #1e1e1e;
    color: #f5f5f5;
    padding: 10px;
    border: none;
    border-radius: 0 12px 12px 0;
    font-family: monospace;
    font-size: 16px;
    line-height: 1.5em;
    white-space: pre;
    overflow: auto;
    resize: none;
    margin-left: 60px;
}

.syntax-check-button, .submit-dag-button {
    padding: 0.5rem;
    background-color: #28a745;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    font-family: 'Poppins', sans-serif;
    margin-top: 1rem;
    align-self: flex-end;
}

.syntax-check-button:hover, .submit-dag-button:hover {
    background-color: #218838;
}

.spinner {
    border: 2px solid #f3f3f3;
    border-top: 2px solid #007bff;
    border-radius: 50%;
    width: 14px;
    height: 14px;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.syntax-check-result {
    margin-top: 1rem;
    font-family: 'Poppins', sans-serif;
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    width: 100%;
    max-width: 770px;
}
</style>
