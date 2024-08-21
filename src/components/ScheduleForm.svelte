<script>
    import axios from 'axios'; // Import axios

    // Dropdown values for cron format, starting from 0 and including '*'

    let promptText = "";

    async function submitSchedule() {
        console.log("Prompt:", promptText);

        // Send the schedule and prompt to your backend
        const payload = {
                        "prompt": promptText
                        }

        console.log("payload json: ", payload);

        try {
            const response = await axios.post('http://localhost:45000/generate_dag', payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('Success:', response.data);
        } catch (error) {
            console.error('Error:', error.message || error);
        }
    }
</script>

<div class="schedule-form">
    <h2>Set Airflow DAG Schedule</h2>
    <label>
        Prompt:
        <input type="text" bind:value={promptText} placeholder="Enter your prompt" />
    </label>

    <button on:click={submitSchedule}>Send</button>
</div>

<style>
    .schedule-form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        max-width: 300px;
        margin: auto;
    }
    label {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    button {
        padding: 0.5rem;
        background-color: #007bff;
        color: white;
        border: none;
        cursor: pointer;
        border-radius: 4px;
    }
    button:hover {
        background-color: #0056b3;
    }
</style>
