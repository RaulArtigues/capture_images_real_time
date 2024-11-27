document.addEventListener("DOMContentLoaded", () => {
    const galleryInput = document.getElementById("galleryInput");
    const galleryImage = document.getElementById("gallery-image");
    const galleryAnalyzeButton = document.getElementById("galleryAnalyzeButton");
    const clearButton = document.getElementById("clearGalleryButton");
    const spinnerContainer = document.getElementById("gallery-spinner-container");
    const arrowGallery = document.getElementById("arrow-gallery");
    const resultadoContainer = document.getElementById("gallery-resultado");

    let imageMetadata = {}; // Objeto para almacenar los metadatos

    // Verifica que los elementos existen
    if (!galleryInput || !galleryImage || !galleryAnalyzeButton || !clearButton) {
        console.error("Error: Algunos elementos del DOM no se encontraron.");
        return;
    }

    // Obtener información del dispositivo
    const deviceInfo = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        pixelRatio: window.devicePixelRatio,
        colorDepth: window.screen.colorDepth,
        touchPoints: navigator.maxTouchPoints,
        cpuCores: navigator.hardwareConcurrency,
    };

    // Mostrar la imagen cargada y extraer metadatos
    galleryInput.addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (!file) {
            alert("No se seleccionó ninguna imagen.");
            return;
        }

        // Verificar tipo de archivo
        console.log("Archivo seleccionado:", file.type);
        if (!file.type.includes("jpeg")) {
            alert("Solo se admiten imágenes JPEG con metadatos EXIF.");
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            galleryImage.src = e.target.result;
            galleryImage.style.display = "block"; // Mostrar la imagen
            galleryAnalyzeButton.style.display = "block"; // Mostrar el botón de analizar
            clearButton.style.display = "block"; // Mostrar el botón de borrar
            resultadoContainer.innerHTML = "<p>Carga una imagen para visualizar los resultados.</p>";
            arrowGallery.style.display = "none"; // Ocultar el texto "Resultados abajo"

            // Leer los metadatos EXIF
            EXIF.getData(file, function () {
                imageMetadata = EXIF.getAllTags(this); // Obtener todos los metadatos
                console.log("Metadatos extraídos:", imageMetadata);

                if (Object.keys(imageMetadata).length === 0) {
                    alert("No se encontraron metadatos EXIF en esta imagen.");
                }
            });
        };
        reader.readAsDataURL(file);
    });

    // Analizar la imagen cargada
    galleryAnalyzeButton.addEventListener("click", async () => {
        const file = galleryInput.files[0];
        if (!file) {
            alert("Debe seleccionar una imagen antes de analizarla.");
            return;
        }

        // Leer el archivo como Base64
        const reader = new FileReader();
        reader.onload = async (e) => {
            const imageBase64 = e.target.result.split(",")[1];

            // Mostrar spinner y ocultar botón de analizar
            spinnerContainer.style.display = "flex";
            galleryAnalyzeButton.style.display = "none";

            try {
                // Llamar al endpoint del backend
                const response = await fetch("/analyze_image_gallery", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        image: imageBase64, // Imagen en formato Base64
                        metadata: imageMetadata, // Metadatos extraídos
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
                    throw new Error(`Error en la respuesta del servidor: ${response.status}`);
                }

                const data = await response.json();

                // Mostrar resultados
                resultadoContainer.innerHTML = `
                <h3><b>Información del Dispositivo:</b></h3>
                <p><strong>User-Agent:</strong> ${data.client_info?.user_agent || "N/A"}</p>
                <p><strong>Platform:</strong> ${data.client_info?.platform || "N/A"}</p>
                <p><strong>Screen Width:</strong> ${data.client_info?.screen_width || "N/A"}</p>
                <p><strong>Screen Height:</strong> ${data.client_info?.screen_height || "N/A"}</p>
                <p><strong>Pixel Ratio:</strong> ${data.client_info?.pixel_ratio || "N/A"}</p>
                <p><strong>Color Depth:</strong> ${data.client_info?.color_depth || "N/A"}</p>
                <p><strong>Touch Points:</strong> ${data.client_info?.touch_points || "N/A"}</p>
                <p><strong>CPU Cores:</strong> ${data.client_info?.cpu_cores || "N/A"}</p>

                <h3><b>Metadata:</b></h3>
                <p><strong>MetaData:</strong> <pre>${JSON.stringify(data.metadata || {}, null, 2)}</pre></p>
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
                arrowGallery.style.display = "block"; // Mostrar el texto "Resultados abajo"
            } catch (error) {
                console.error("Error durante el análisis:", error);
                alert("Ocurrió un error al procesar la imagen.");
            } finally {
                spinnerContainer.style.display = "none"; // Ocultar el spinner
                galleryAnalyzeButton.style.display = "block"; // Mostrar botón nuevamente
            }
        };
        reader.readAsDataURL(file);
    });

    // Borrar la imagen y los resultados
    clearButton.addEventListener("click", () => {
        galleryImage.style.display = "none";
        galleryImage.src = "";
        galleryAnalyzeButton.style.display = "none";
        resultadoContainer.innerHTML = "<p>Carga una imagen para visualizar los resultados.</p>";
        clearButton.style.display = "none"; // Ocultar el botón de borrar
        arrowGallery.style.display = "none"; // Ocultar el texto "Resultados abajo"
        imageMetadata = {}; // Limpiar los metadatos
    });
});

// Borrar la imagen y los resultados
clearButton.addEventListener("click", () => {
    galleryImage.style.display = "none";
    galleryImage.src = "";
    galleryAnalyzeButton.style.display = "none";
    resultadoContainer.innerHTML = "<p>Carga una imagen para visualizar los resultados.</p>";
    clearButton.style.display = "none"; // Ocultar el botón de borrar
    arrowGallery.style.display = "none"; // Ocultar el texto "Resultados abajo"
    imageMetadata = {}; // Limpiar los metadatos
});