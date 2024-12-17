document.getElementById('toggleButton').addEventListener('click', function () {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    sidebar.classList.toggle('active');

    if (sidebar.classList.contains('active')) {
        content.style.marginLeft = '250px';
    } else {
        content.style.marginLeft = '0';
    }
});