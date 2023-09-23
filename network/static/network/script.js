let nots = fetch('/notifications')
.then(res => res.json())
.then(data=>console.log(data))
const like = document.querySelectorAll(".liked");
const comment_like = document.querySelectorAll('.like-comment')
const edit = document.querySelectorAll(".edit");
const text_area = document.querySelectorAll(".textarea");
for (const element of like) {
  like_handeler(element);
}
for (const element of comment_like) {
  comment_like_handler(element);
}
for (const element of edit) {
  element.addEventListener("click", () => {
    edit_handler(element);
  });
}
for (const element of text_area) {
  element.addEventListener("keyup", (e) => {
    if (e.keyCode == 13 && e.shiftKey) return;
    if (e.keyCode === 13) edit_handler(element);
  });
}
function edit_post(id, post) {
  const form = new FormData();
  form.append("id", id);
  form.append("post", post.trim());
  fetch("/edit_post/", {
    method: "POST",
    body: form,
  }).then((res) => {
    document.querySelector(`#post-content-${id}`).textContent = post;
    document.querySelector(`#post-content-${id}`).style.display = "block";
    document.querySelector(`#post-edit-${id}`).style.display = "none";
    document.querySelector(`#post-edit-${id}`).value = post.trim();
  });
}
function edit_handler(element) {
  const { id } = element.dataset;
  const edit_btn = document.querySelector(`#edit-btn-${id}`);
  if (edit_btn.textContent == "Edit") {
    document.querySelector(`#post-content-${id}`).style.display = "none";
    document.querySelector(`#post-edit-${id}`).style.display = "block";
    edit_btn.textContent = "Save";
    edit_btn.setAttribute("class", "text-success edit");
  } else if (edit_btn.textContent == "Save") {
    edit_post(id, document.querySelector(`#post-edit-${id}`).value);
    edit_btn.textContent = "Edit";
    edit_btn.setAttribute("class", "text-primary edit");
  }
}
function like_handeler(element, type) {
  element.addEventListener("click", () => {
    const { id, is_liked } = element.dataset;
    const icon = document.querySelector(`#post-like-${id}`);
    const count = document.querySelector(`#post-count-${id}`);
    const form = new FormData();
    form.append("id", id);
    form.append("is_liked", is_liked);
    fetch("/like/", {
      method: "POST",
      body: form,
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.status == 201) {
          element.dataset.is_liked = res.is_liked;
          count.textContent = res.like_count;
        }
      })
      .catch(function (res) {
        alert("Network Error. Please Check your connection.");
      });
  });
}
function comment_like_handler(element){
  element.addEventListener("click", () => {
    const { id, is_liked } = element.dataset;
    const count = document.querySelector(`#comment-count-${id}`);
    const form = new FormData();
    form.append("comment_id", id);
    form.append("is_liked", is_liked);
    fetch("/comment/like/", {
      method: "POST",
      body: form,
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.status == 201) {
          element.dataset.is_liked = res.is_liked;
          count.textContent = res.like_count;
        }
      })
      .catch(function (res) {
        alert("Network Error. Please Check your connection.");
      });
  });
}