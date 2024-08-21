<script>
    import axios from 'axios'; // Import axios

    let promptText = "";

    async function submitSchedule() {
        console.log("Prompt:", promptText);

        const payload = {
            "prompt": promptText
        };

        console.log("Payload JSON:", payload);

        try {
            const response = await axios.post('http://127.0.0.1:45000/generate_dag', payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('Response Data:', response.data);
            // Display response data in your application, e.g., update a state or an element
            alert('Response received: ' + response.data.code); // Example of displaying response data
        } catch (error) {
            console.error('Error:', error.message || error);
            alert('Error occurred: ' + (error.message || error));
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
