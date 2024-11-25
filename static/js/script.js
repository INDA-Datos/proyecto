document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('upload-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData();
        const fileInput = document.getElementById('file-input');
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                document.getElementById('result').innerHTML = `<p>${result.message}</p>`;

                const statsDiv = document.getElementById('stats');
                statsDiv.innerHTML = `<h2>Estadísticas:</h2><pre>${JSON.stringify(result.stats, null, 2)}</pre>`;

                const graph = document.getElementById('graph');
                graph.src = result.graph_url;
                graph.style.display = 'block';

                const downloadButton = document.getElementById('download-button');
                downloadButton.style.display = 'block';
                downloadButton.onclick = () => {
                    window.location.href = result.download_url;
                };
            } else {
                document.getElementById('result').innerHTML = `<p>Error: ${result.error}</p>`;
            }
        } catch (error) {
            document.getElementById('result').innerHTML = `<p>Error: ${error.message}</p>`;
        }
    });
});
