<script>
    import axios from 'axios'; // Import axios

    let promptText = "";
    let pyodide;
    let pyodideLoaded = false;
    let errorMessage = '';
    let code = '';
    let isLoading = false;
    let syntaxCheckResult = ''; // Variable to store the result of syntax check
    let showSyntaxCheckResult = false; // Flag to control visibility of syntax check result

    async function loadPyodide() {
        try {
            // Load Pyodide
            if (!window.loadPyodide) {
                throw new Error('Pyodide script not loaded');
            }
            pyodide = await window.loadPyodide();
            await pyodide.loadPackage('micropip'); // To use micropip if needed
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
        console.log("Prompt:", promptText);

        const payload = {
            "prompt": promptText
        };

        console.log("Payload JSON:", payload);
        isLoading = true; // Show spinner

        try {
            const response = await axios.post('http://127.0.0.1:45000/generate_dag', payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('Response Data:', response.data);
            code = response.data.code;

            // Strip Markdown formatting if present
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
            isLoading = false; // Hide spinner
        }
    }

    async function checkSyntax() {
        if (pyodideLoaded) {
            try {
                // Check for syntax errors using ast module
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
                syntaxCheckResult = result; // Store the result
                showSyntaxCheckResult = true; // Show syntax check result
                console.log('Syntax Check Result:', result); // Debugging
            } catch (error) {
                syntaxCheckResult = 'Error in Python code: ' + error.message;
                showSyntaxCheckResult = true; // Show syntax check result
                console.error('Error in Python code:', error); // Debugging
            }
        } else {
            syntaxCheckResult = 'Pyodide is not loaded yet';
            showSyntaxCheckResult = true; // Show syntax check result
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
            <input type="text" bind:value={promptText} placeholder="Enter your prompt" />
        </label>
        <button class="submit-button" on:click={submitSchedule} disabled={isLoading}>
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
            <button class="syntax-check-button" on:click={checkSyntax}>Is the DAG executable</button>
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
    gap: 1rem; /* Added gap to create space between input and button */
    margin-bottom: 1rem;
}

.prompt-label {
    flex: 1; /* Makes the input field take as much space as possible */
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.prompt-label input {
    width: 95%; /* Ensures the input field takes up the full width of its container */
    padding: 0.5rem;
    font-family: 'Poppins', sans-serif; /* Apply Poppins font */
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem; /* Adjust font size if needed */
}

.submit-button {
    padding: 0.5rem 1rem; /* Adjusted padding for better button size */
    font-size: 0.875rem; /* Adjust font size for the button */
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    font-family: 'Poppins', sans-serif; /* Apply Poppins to button text */
    white-space: nowrap; /* Prevent text from wrapping */
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

.syntax-check-button {
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

.syntax-check-button:hover {
    background-color: #218838;
}

.spinner {
    border: 2px solid #f3f3f3;
    border-top: 2px solid #007bff;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    margin-right: 8px;
    animation: spin 1s linear infinite;
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

