// Función para inicializar la cámara
async function initCamera() {
    try {
        const video = document.getElementById("video");

        // Verificar compatibilidad de la API
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Este navegador no soporta acceso a la cámara.");
            return;
        }

        // Configuración para capturar en la resolución máxima de la cámara trasera
        const constraints = {
            video: {
                facingMode: "environment",
                width: { ideal: 4096 }, // Idealmente intenta capturar la resolución máxima
                height: { ideal: 2160 }
            }
        };

        // Acceder al flujo de la cámara
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;
        window.stream = stream;

        // Esperar hasta que el video esté listo
        await new Promise((resolve) => {
            video.onloadedmetadata = () => {
                console.log(`Resolución del video: ${video.videoWidth}x${video.videoHeight}`);
                resolve();
            };
        });

    } catch (error) {
        console.error("Error al intentar acceder a la cámara:", error);
        alert("No se pudo acceder a la cámara. Verifica los permisos y la configuración del navegador.");
    }
}

// Función para capturar la imagen
async function captureImage() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const context = canvas.getContext("2d");

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Dibujar la imagen en el canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convertir la imagen a formato Base64
        const imageBase64 = canvas.toDataURL("image/jpeg", 1).split(",")[1];

        // Mostrar la imagen capturada para inspección visual
        const img = document.createElement("img");
        img.src = canvas.toDataURL("image/jpeg", 1.0);
        img.style.width = "200px"; // Ajustar el tamaño para mostrar como miniatura
        img.style.margin = "10px";
        document.body.appendChild(img);

        // Enviar la imagen al servidor
        try {
            const response = await fetch("/analyze_image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image: imageBase64 })
            });

            if (!response.ok) {
                throw new Error("Error en la respuesta del servidor");
            }

            const data = await response.json();

            // Mostrar los resultados
            document.getElementById("resultado").innerHTML = `
            <h3>Resultados del Análisis:</h3>
            <p><strong>ID Imagen:</strong> ${data.image_id || "N/A"}</p>
            <p><strong>Dimensiones Originales:</strong> 
            ${data.original_dimensions?.width || "N/A"}x${data.original_dimensions?.height || "N/A"}</p>
            <p><strong>Dimensiones Redimensionadas:</strong> 
            ${data.resized_dimensions?.width || "N/A"}x${data.resized_dimensions?.height || "N/A"}</p>

            <p><strong>Nitidez:</strong> ${data.sharpness?.sharpness_value?.toFixed(4) || "N/A"} 
            (${data.sharpness?.is_valid ? "Válida" : "No válida"})</p>

            <p><strong>Exposición (Sobreexpuesta):</strong> 
            ${data.exposure?.overexposed_percentage?.toFixed(2) || "N/A"}% 
            (${data.exposure?.is_overexposed_valid ? "Válida" : "No válida"})</p>

            <p><strong>Exposición (Subexpuesta):</strong> 
            ${data.exposure?.underexposed_percentage?.toFixed(2) || "N/A"}% 
            (${data.exposure?.is_underexposed_valid ? "Válida" : "No válida"})</p>

            <p><strong>Exposición General:</strong> 
            ${data.exposure?.is_valid ? "Válida" : "No válida"}</p>

            <p><strong>NIQE:</strong> ${data.niqe?.niqe_score?.toFixed(4) || "N/A"} 
            (${data.niqe?.niqe_quality || "N/A"})</p>

            <p><strong>PIQA:</strong> ${data.piqa?.piqa_score?.toFixed(4) || "N/A"} 
            (${data.piqa?.piqa_quality || "N/A"})</p>

            <p><strong>Tiempo de Procesamiento:</strong> 
            ${data.processing_time_seconds?.toFixed(4) || "N/A"} s 
            (${data.processing_time_milliseconds?.toFixed(2) || "N/A"} ms)</p>

            <p><strong>Ruta de la Imagen Guardada:</strong> 
            ${data.saved_path || "N/A"}</p>
            `;
        } catch (error) {
            console.error("Error al enviar la imagen:", error);
            alert("Ocurrió un error al procesar la imagen.");
        }

        // Reiniciar el sistema para la próxima captura
        resetCapture();
    } else {
        alert("La cámara no está lista. Inténtalo nuevamente.");
    }
}

// Función para reiniciar la captura
function resetCapture() {
    stopCamera(); // Detener la cámara
    initCamera(); // Volver a inicializar la cámara
}

// Función para detener la cámara
function stopCamera() {
    if (window.stream) {
        window.stream.getTracks().forEach(track => track.stop());
        window.stream = null;
    }
}

// Iniciar la cámara cuando se carga la página
window.addEventListener("load", initCamera);

// Agregar el evento de captura de imagen al botón
document.getElementById("capture").addEventListener("click", captureImage);