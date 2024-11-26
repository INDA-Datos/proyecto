document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("file-input");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("/process_data", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            const kpiContainer = document.getElementById("kpi-container");
            kpiContainer.innerHTML = "";

            Object.keys(data).forEach((key) => {
                const kpiBox = document.createElement("div");
                kpiBox.className = "kpi-box";
                kpiBox.innerHTML = `
                    <h3>${key}</h3>
                    <p>${data[key]}</p>
                `;
                kpiContainer.appendChild(kpiBox);
            });
        } else {
            alert(data.error || "Ocurrió un error procesando los datos.");
        }
    } catch (error) {
        alert("Error al procesar los datos.");
        console.error(error);
    }
});
