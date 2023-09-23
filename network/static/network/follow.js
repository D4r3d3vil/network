const follow_btn = document.querySelector("#follow-btn");
follow_btn.addEventListener("click", async (e) => {
  const { user } = follow_btn.dataset;
  const form = new FormData();
  form.append("user", user);
  form.append("action", follow_btn.innerText);
  try {
    const res = await fetch("/follow/", {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    if (data.status == 201) {
      follow_btn.textContent = data.action;
      document.querySelector(
        "#follower"
      ).textContent = `Followers ${data.follower_count}`;
    }
  } catch (error) {
    console.error(error);
  }
});
