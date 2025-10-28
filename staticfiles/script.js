// window.addEventListener("scroll", function () {
//         const header = document.querySelector("header");
//         if (window.scrollY > 50) {
//           header.classList.add("shrink");
//         } else {
//           header.classList.remove("shrink");
//         }
//       });
    

//     //   caresol

// const track = document.getElementById("carousel-track");
// // const slides = Array.from(track.children);
// const prevBtn = document.getElementById("prev");
// const nextBtn = document.getElementById("next");
// const indicatorsContainer = document.getElementById("carousel-indicators");

// let index = 0;
// let autoPlayInterval;

// // Create indicators
// slides.forEach((_, i) => {
//   const dot = document.createElement("div");
//   dot.classList.add("medical-sec3-inner-indicator");
//   if (i === 0) dot.classList.add("active");
//   dot.addEventListener("click", () => goToSlide(i));
//   indicatorsContainer.appendChild(dot);
// });
// const indicators = indicatorsContainer.querySelectorAll(".medical-sec3-inner-indicator");

// // Update carousel view
// function updateCarousel() {
//   track.style.transform = `translateX(-${index * 100}%)`;

//   slides.forEach((slide, i) =>
//     slide.classList.toggle("active", i === index)
//   );

//   indicators.forEach((dot, i) =>
//     dot.classList.toggle("active", i === index)
//   );
// }

// function goToSlide(i) {
//   index = i;
//   updateCarousel();
//   resetAutoplay();
// }

// function nextSlide() {
//   index = (index + 1) % slides.length;
//   updateCarousel();
// }

// function prevSlide() {
//   index = (index - 1 + slides.length) % slides.length;
//   updateCarousel();
// }

// prevBtn.addEventListener("click", prevSlide);
// nextBtn.addEventListener("click", nextSlide);

// // Autoplay
// function startAutoplay() {
//   autoPlayInterval = setInterval(nextSlide, 4000);
// }
// function stopAutoplay() {
//   clearInterval(autoPlayInterval);
// }
// function resetAutoplay() {
//   stopAutoplay();
//   startAutoplay();
// }

// // Only start autoplay when carousel is in view
// const carouselSection = document.querySelector(".medical-sec3");
// const observer = new IntersectionObserver(
//   (entries) => {
//     entries.forEach((entry) => {
//       if (entry.isIntersecting) {
//         startAutoplay();
//       } else {
//         stopAutoplay();
//       }
//     });
//   },
//   { threshold: 0.5 }
// );
// observer.observe(carouselSection);

// // Initial
// updateCarousel();



