document.addEventListener("DOMContentLoaded", () => {
    const bookTitleInput = document.getElementById("book-title");
    const searchBtn = document.getElementById("search-btn");
    const resultsContainer = document.getElementById("results-container");

    searchBtn.addEventListener("click", async () => {
        const title = bookTitleInput.value.trim();
        if (!title) {
            alert("Please enter a book title.");
            return;
        }

        resultsContainer.innerHTML = "<p>Loading...</p>";

        try {
            const response = await fetch(`/recommend?title=${encodeURIComponent(title)}`);
            const data = await response.json();

            if (data.error) {
                resultsContainer.innerHTML = `<p>Error: ${data.error}</p>`;
                return;
            }

            let html = "";
            if (data.original_book) {
                html += "<h2>Original Book</h2>";
                html += renderBook(data.original_book);
            }

            if (data.recommendations && data.recommendations.length > 0) {
                html += "<h2>Recommendations</h2>";
                data.recommendations.forEach(book => {
                    html += renderBook(book);
                });
            }

            resultsContainer.innerHTML = html;

        } catch (error) {
            resultsContainer.innerHTML = "<p>An unexpected error occurred.</p>";
            console.error(error);
        }
    });

    function renderBook(book) {
        let authorsHtml = book.author ? `<p class="book-authors">${book.author}</p>` : '';
        let subjectsHtml = book.subjects && book.subjects.length > 0 ? `<p class="book-subjects">Subjects: ${book.subjects.join(', ')}</p>` : '';

        // Check if it's the original book (it won't have a 'distance' property)
        if (!book.distance) {
            // For original book, we only show title and subjects (if available)
            return `
                <div class="book">
                    <p class="book-title">${book.title}</p>
                    ${authorsHtml}
                    ${subjectsHtml}
                </div>
            `;
        } else {
            // For recommended books, show title, author, subjects, and distance
            return `
                <div class="book">
                    <p class="book-title">${book.title}</p>
                    ${authorsHtml}
                    ${subjectsHtml}
                    <p class="book-distance">Distance: ${book.distance.toFixed(4)}</p>
                </div>
            `;
        }
    }
});
