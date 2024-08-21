<script>
    import { onMount } from 'svelte';
    import { EditorView, basicSetup } from 'codemirror';
    import { python } from '@codemirror/lang-python';

    let editor;

    onMount(() => {
        editor = new EditorView({
            doc: 'print("Hello, world!")', // initial content
            extensions: [basicSetup, python()],
            parent: document.querySelector('#editor'),
        });
    });

    export let code = '';

    function executeCode() {
        code = editor.state.doc.toString();
        console.log('Executing code:', code);
        // Your code execution logic here
    }
</script>

<div id="editor" style="border: 1px solid #ccc; height: 300px;"></div>
<button on:click={executeCode}>Execute Code</button>
