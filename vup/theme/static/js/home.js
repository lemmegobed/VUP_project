<!-- เปลี่ยนไอคอนเป็นย้อนกลับ -->

    document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const searchIcon = document.getElementById('search-icon');
    const searchForm = document.getElementById('search-form');

    // เมื่อผู้ใช้เริ่มพิมพ์
    searchInput.addEventListener('input', function () {
        if (searchInput.value.trim() !== '') {
            // ถ้ามีข้อความในช่องค้นหา เปลี่ยนไอคอนเป็นย้อนกลับ
            searchIcon.classList.remove('fa-search');
            searchIcon.classList.add('fa-arrow-left');
            searchIcon.style.cursor = 'pointer';

            // เพิ่มการคลิกที่ไอคอนเพื่อย้อนกลับไปหน้าแรก
            searchIcon.onclick = function () {
                window.location.href = "{% url 'home' %}"; // ย้อนกลับไปหน้าแรก
            };
        } else {
            // ถ้าไม่มีข้อความ เปลี่ยนไอคอนกลับเป็นค้นหา
            searchIcon.classList.remove('fa-arrow-left');
            searchIcon.classList.add('fa-search');
            searchIcon.style.cursor = 'default';
            searchIcon.onclick = null; // ลบการคลิก
        }
    });

    // เมื่อกด Enter ในช่องค้นหา
    searchInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // ป้องกันการ reload
            searchForm.submit(); // ส่งฟอร์ม
        }
    });
});



<!-- new_event -->

    const openModal = document.getElementById("openModal");
    const modal = document.getElementById("eventModal");
    const closeModal = document.querySelector(".close");
    const eventForm = document.getElementById('eventForm');
    const homePageDiv = document.getElementById('home_page');

    openModal.onclick = function() {
        modal.classList.add("active");
    }

    closeModal.onclick = function() {
        modal.classList.remove("active");
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.classList.remove("active");
        }
    }

    eventForm.addEventListener('submit', function(e) {
        e.preventDefault();  // ป้องกันการส่งฟอร์มแบบปกติ

        const formData = new FormData(eventForm);
        fetch("{% url 'new_event' %}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modal.classList.remove("active");  // ปิด pop-up
                window.location.reload();  // รีเฟรชหน้าเว็บเพื่อแสดง Event ใหม่
            }
        })
        .catch(error => console.log('Error:', error));
    });


       

            // เปิด modal สำหรับแก้ไข event
            function toggleDropdownMenu(eventId) {
    // Log เพื่อดูว่า function ถูกเรียกใช้หรือไม่
    console.log("Toggling dropdown for event:", eventId);
    var dropdown = document.getElementById("dropdownMenu-" + eventId);
    dropdown.style.display = (dropdown.style.display === "block") ? "none" : "block";
}

// ปิด dropdown เมื่อลงคลิกนอก dropdown
window.onclick = function(event) {
    if (!event.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
            menu.style.display = "none";
        });
    }
};





function openEditModal(eventId) {
    // ตั้งค่า action URL สำหรับฟอร์มแก้ไข event
    const modal = document.getElementById('editEventModal');
    modal.classList.add("active");  // แสดง modal

    // ดึงข้อมูลกิจกรรมที่ต้องการแก้ไข
    fetch(`/update_event/${eventId}/`)
        .then(response => response.json())
        .then(data => {
            // ตั้งค่าฟิลด์ในฟอร์มด้วยข้อมูลที่ได้
            document.getElementById('edit_event_name').value = data.event_name;
            document.getElementById('edit_event_title').value = data.event_title;
            document.getElementById('edit_event_datetime').value = data.event_datetime;
            document.getElementById('edit_location').value = data.location;
            document.getElementById('edit_category').value = data.category;
            document.getElementById('edit_max_participants').value = data.participants;
            document.getElementById('edit_province').value = data.province;

            // กำหนด action ของฟอร์มให้ถูกต้อง
            document.getElementById('editEventForm').action = `/update_event/${eventId}/`;
        })
        .catch(error => console.error('Error:', error));
}

function closeModal() {
    const modal = document.getElementById('editEventModal');
    modal.classList.remove("active");
}




        let deleteEventId = null;

    function openConfirmDeleteModal(eventId) {
        deleteEventId = eventId;
        document.getElementById('confirmDeleteModal').classList.add('active');
    }

    function closeConfirmDeleteModal() {
        deleteEventId = null;
        document.getElementById('confirmDeleteModal').classList.remove('active');
    }

    document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
        if (deleteEventId) {
            // ส่งฟอร์มเพื่อทำการลบ event
            const deleteForm = document.getElementById('deleteForm-' + deleteEventId);
            deleteForm.submit();
        }
    });

