let hayResultadosPrevios = false; // Bandera para rastrear si hay resultados previos

// Obtener información del dispositivo
let deviceInfo = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    screenWidth: window.screen.width,
    screenHeight: window.screen.height,
    pixelRatio: window.devicePixelRatio,
    colorDepth: window.screen.colorDepth,
    touchPoints: navigator.maxTouchPoints,
    cpuCores: navigator.hardwareConcurrency,
};

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
                width: { ideal: 4096 },
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
    const spinnerContainer = document.getElementById("spinner-container");
    const clearButton = document.getElementById("clearButton");
    const arrow = document.getElementById("arrow");

    // Si hay resultados previos, limpiarlos antes de capturar la nueva imagen
    if (hayResultadosPrevios) {
        clearPreviousResults();
    }

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Dibujar la imagen en el canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convertir la imagen a formato Base64
        const imageBase64 = canvas.toDataURL("image/jpeg", 1).split(",")[1];

        // Mostrar la imagen capturada dentro del contenedor #resultado
        const resultadoDiv = document.getElementById("resultado");
        const img = document.createElement("img");
        img.src = canvas.toDataURL("image/jpeg", 1.0);
        img.style.width = "200px"; // Ajustar el tamaño para mostrar como miniatura
        img.style.margin = "10px auto";
        img.style.display = "block"; // Centrar la imagen
        img.classList.add("captured-image"); // Añadir clase para identificación
        resultadoDiv.appendChild(img); // Añadir la imagen al contenedor #resultado

        // Mostrar el spinner mientras se procesan los resultados
        spinnerContainer.style.display = "flex";
        arrow.style.display = "none"; // Asegurarse de que la flecha esté oculta
        clearButton.style.display = "block"; // Mostrar el botón de borrar

        // Enviar la imagen al servidor
        try {

            const response = await fetch("/analyze_image_real_time", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    image: imageBase64,
                    userAgent: deviceInfo.userAgent,
                    platform: deviceInfo.platform,
                    screenWidth: deviceInfo.screenWidth,
                    screenHeight: deviceInfo.screenHeight,
                    pixelRatio: deviceInfo.pixelRatio,
                    colorDepth: deviceInfo.colorDepth,
                    touchPoints: deviceInfo.touchPoints,
                    cpuCores: deviceInfo.cpuCores,
                })
            });

            if (!response.ok) {
                throw new Error("Error en la respuesta del servidor");
            }

            const data = await response.json();

            // Mostrar los resultados dentro de #resultado
            resultadoDiv.innerHTML += `
            <h3><b>Información del Dispositivo:</b></h3>
            <p><strong>User-Agent:</strong> ${data.client_info?.user_agent || "N/A"}</p>
            <p><strong>Platform:</strong> ${data.client_info?.platform || "N/A"}</p>
            <p><strong>Screen Width:</strong> ${data.client_info?.screen_width || "N/A"}</p>
            <p><strong>Screen Height:</strong> ${data.client_info?.screen_height || "N/A"}</p>
            <p><strong>Pixel Ratio:</strong> ${data.client_info?.pixel_ratio || "N/A"}</p>
            <p><strong>Color Depth:</strong> ${data.client_info?.color_depth || "N/A"}</p>
            <p><strong>Touch Points:</strong> ${data.client_info?.touch_points || "N/A"}</p>
            <p><strong>CPU Cores:</strong> ${data.client_info?.cpu_cores || "N/A"}</p>

            <h3><b>Resultados del Análisis:</b></h3>
            <p><strong>ID Imagen:</strong> ${data.image_id || "N/A"}</p>
            <p><strong>Dimensiones Originales:</strong> 
            ${data.original_dimensions?.width || "N/A"}x${data.original_dimensions?.height || "N/A"}</p>
            <p><strong>Dimensiones Redimensionadas:</strong> 
            ${data.resized_dimensions?.width || "N/A"}x${data.resized_dimensions?.height || "N/A"}</p>

            <p><strong>Nitidez:</strong> ${data.sharpness?.sharpness_value?.toFixed(4) || "N/A"} 
            (${data.sharpness?.is_correct_sharpness ? "Válida" : "No válida"})</p>

            <p><strong>Exposición (Sobreexpuesta):</strong> 
            ${data.exposure?.overexposed_percentage?.toFixed(2) || "N/A"}% 
            (${data.exposure?.is_overexposed_correct ? "Válida" : "No válida"})</p>

            <p><strong>Exposición (Subexpuesta):</strong> 
            ${data.exposure?.underexposed_percentage?.toFixed(2) || "N/A"}% 
            (${data.exposure?.is_underexposed_correct ? "Válida" : "No válida"})</p>

            <p><strong>Exposición General:</strong> 
            ${data.exposure?.is_correct_exposure ? "Válida" : "No válida"}</p>

            <p><strong>Reflejo Especular:</strong> 
            ${data.specular_reflections?.specular_score?.toFixed(2) || "N/A"}% 
            (${data.specular_reflections?.is_correct_specular_reflections ? "Válida" : "No válida"})</p>

            <p><strong>Tiempo de Procesamiento:</strong> 
            ${data.processing_time_seconds?.toFixed(4) || "N/A"} s 
            (${data.processing_time_milliseconds?.toFixed(2) || "N/A"} ms)</p>

            <p><strong>Ruta de la Imagen Guardada:</strong> 
            ${data.saved_path || "N/A"}</p>
            `;
        } catch (error) {
            console.error("Error al enviar la imagen:", error);
            alert("Ocurrió un error al procesar la imagen.");
        } finally {
            // Ocultar el spinner y mostrar la flecha
            spinnerContainer.style.display = "none";
            arrow.style.display = "block";
        }

        // Actualizar la bandera indicando que ahora hay resultados previos
        hayResultadosPrevios = true;
    } else {
        alert("La cámara no está lista. Inténtalo nuevamente.");
    }
}

// Función para limpiar resultados previos
function clearPreviousResults() {
    const resultadoDiv = document.getElementById("resultado");
    resultadoDiv.innerHTML = ""; // Limpia los resultados
    const previousImages = document.querySelectorAll(".captured-image");
    previousImages.forEach(img => img.remove());
}

// Borrar la imagen y los resultados
document.addEventListener("DOMContentLoaded", () => {
    const clearButton = document.getElementById("clearButton");
    const arrow = document.getElementById("arrow");
    const resultadoDiv = document.getElementById("resultado");

    clearButton.addEventListener("click", () => {
        resultadoDiv.innerHTML = "<p>Carga una imagen para visualizar los resultados.</p>";
        const previousImages = document.querySelectorAll(".captured-image");
        previousImages.forEach(img => img.remove());
        clearButton.style.display = "none";
        arrow.style.display = "none";
        hayResultadosPrevios = false; // Reinicia la bandera
    });
});

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