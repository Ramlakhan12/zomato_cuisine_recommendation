function search() {
    let query = document.querySelector('.search-bar input').value;
    if (query) {
        alert(`Searching for "${query}"...`);
    } else {
        alert("Please enter a search term!");
    }
}
