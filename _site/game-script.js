// Get the canvas element and set its size
const canvas = document.getElementById('gameCanvas');
const gl = canvas.getContext('webgl');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Clear the canvas
gl.clearColor(0.0, 0.0, 0.0, 1.0);
gl.clear(gl.COLOR_BUFFER_BIT);

// Create a simple square (arena) as a placeholder
const vertices = new Float32Array([
    -0.5, 0.5, 0.0, // Top left
    0.5, 0.5, 0.0,  // Top right
    0.5, -0.5, 0.0, // Bottom right
    -0.5, -0.5, 0.0 // Bottom left
]);

// Create a buffer and put the vertices in it
const vertexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

// Create a simple vertex shader
const vertexShaderSource = `
    attribute vec3 coordinates;
    void main(void) {
        gl_Position = vec4(coordinates, 1.0);
    }
`;
const vertexShader = gl.createShader(gl.VERTEX_SHADER);
gl.shaderSource(vertexShader, vertexShaderSource);
gl.compileShader(vertexShader);

// Create a simple fragment shader
const fragmentShaderSource = `
    void main(void) {
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); // Red color
    }
`;
const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
gl.shaderSource(fragmentShader, fragmentShaderSource);
gl.compileShader(fragmentShader);

// Create a shader program
const shaderProgram = gl.createProgram();
gl.attachShader(shaderProgram, vertexShader);
gl.attachShader(shaderProgram, fragmentShader);
gl.linkProgram(shaderProgram);
gl.useProgram(shaderProgram);

// Bind the vertex buffer
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
const coordinates = gl.getAttribLocation(shaderProgram, 'coordinates');
gl.vertexAttribPointer(coordinates, 3, gl.FLOAT, false, 0, 0);
gl.enableVertexAttribArray(coordinates);

// Draw the arena (a simple square)
gl.viewport(0, 0, canvas.width, canvas.height);
gl.clear(gl.COLOR_BUFFER_BIT);
gl.drawArrays(gl.TRIANGLE_FAN, 0, 4);
