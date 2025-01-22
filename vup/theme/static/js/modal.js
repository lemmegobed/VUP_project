function openJoinModal() {
    document.getElementById("join-modal").style.display = "flex";
}

function closeJoinModal() {
    document.getElementById("join-modal").style.display = "none";
}

function confirmJoin(eventId) {
    fetch(`/event/${eventId}/join/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
            "Content-Type": "application/json",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
            closeJoinModal();
        })
        .catch((error) => console.error("Error:", error));
}
