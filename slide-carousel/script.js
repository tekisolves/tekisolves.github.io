const slider = document.getElementById("slider");
const image2 = document.querySelector(".image2");
const body = document.body;

slider.addEventListener("input", (e) => {
    const value = e.target.value;

    // Adjust the clip-path based on slider value
    image2.style.clipPath = `polygon(0 0, ${value}% 0, ${value}% 100%, 0 100%)`;

    // Change background color dynamically based on slider value
    const red = Math.floor((255 * value) / 100);
    const green = Math.floor((100 * value) / 100);
    const blue = Math.floor((200 * (100 - value)) / 100);

    body.style.backgroundColor = `rgb(${red}, ${green}, ${blue})`;
});
