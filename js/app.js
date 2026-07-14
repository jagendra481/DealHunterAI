const searchBox = document.getElementById("searchBox");

const suggestions = document.getElementById("suggestions");

if (searchBox) {

    searchBox.addEventListener("keyup", async () => {

        const q = searchBox.value;

        if (q.length < 2) {

            suggestions.innerHTML = "";

            return;

        }

        const response = await fetch(`/api/search?q=${encodeURIComponent(q)}`);

        const products = await response.json();

        suggestions.innerHTML = "";

        products.forEach(product => {

            suggestions.innerHTML += `

                <a
                    href="/products"
                    class="list-group-item list-group-item-action">

                    ${product.name}

                </a>

            `;

        });

    });

}
