const text_f = document.querySelector("#add-text");
const btn = document.querySelector("#add-btn");
const root = document.querySelector("#root");
btn.addEventListener("click", async () => {
  const text = text_f.value.trim();
  if (text) {
    const form = new FormData();
    form.append("post", text);
    try {
      const res = await fetch("/addpost/", {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (data.status == 201) {
        add_html(
          data.post_id,
          data.username,
          text,
          data.timestamp,
          `/u/${data.username}`
        );
        text_f.value = "";
      }
    } catch (error) {
      console.error(error);
    }
  }
});
function create_html(id, username, post, time, link) {
  return `
<div class="card my-2" themed noLoutline>
<div class="card-body my-card">
<div class="d-flex mb-2">
<div class="d-flex justify-content-start">
<a href="${link}">
<span class="text-secondary">you</span>
</a>
</div>
<div class="w-100 d-flex justify-content-end">
<span class="mx-2 text-secondary">${time}</span>
<span class="text-primary edit" data-id="${id}" id="edit-btn-${id}">Edit</span>
</div>
</div>
<span class="post" id="post-content-${id}">${post}</span>
<textarea class="form-control textarea" id="post-edit-${id}" data-id="${id}" style="display:none;">${post}</textarea>
<div class="like mt-3">
<svg class="liked" data-id="${id}" id="post-like-${id}" data-is_liked="yes">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 6.00019C10.2006 3.90317 7.19377 3.2551 4.93923 5.17534C2.68468 7.09558 2.36727 10.3061 4.13778 12.5772C5.60984 14.4654 10.0648 18.4479 11.5249 19.7369C11.6882 19.8811 11.7699 19.9532 11.8652 19.9815C11.9483 20.0062 12.0393 20.0062 12.1225 19.9815C12.2178 19.9532 12.2994 19.8811 12.4628 19.7369C13.9229 18.4479 18.3778 14.4654 19.8499 12.5772C21.6204 10.3061 21.3417 7.07538 19.0484 5.17534C16.7551 3.2753 13.7994 3.90317 12 6.00019Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
<span id="post-count-${id}">0</span>
<svg onclick="openTweet(${id})" class="comment_circle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-message-circle"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
</div>
</div>
</div>
  `;
}
function add_html(id, username, post, time, link) {
  const temp = document.createElement("div");
  temp.innerHTML = create_html(id, username, post, time, link);
  const edit_btn = temp.querySelector(`#edit-btn-${id}`);
  const textarea = temp.querySelector(`#post-edit-${id}`);
  edit_btn.addEventListener("click", () => {
    edit_handeler(edit_btn);
  });
  textarea.addEventListener("keyup", (e) => {
    if (e.keyCode == 13 && e.shiftKey) return;
    if (e.keyCode === 13) edit_handeler(textarea);
  });
  const like_btn = temp.querySelector(`#post-like-${id}`);
  like_handeler(like_btn);
  root.appendChild(temp);
  renderTheme()
}