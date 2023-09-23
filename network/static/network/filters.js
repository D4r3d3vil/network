let mostliked, mostcommented, mostrecent
mostrecent = `${window.location.href.replace('?filter=likes', '').replace('&filter=likes', '').replace('?filter=comment', '').replace('&filter=comment', '')}`
if(window.location.href.includes('filter=comment')){ 
  mostliked = `${window.location.href.replace('filter=comment', 'filter=likes')}` 
}else{
  mostliked = `${window.location.href}${window.location.href.includes('?')?'&':'?'}filter=likes`
}
if(window.location.href.includes('filter=likes')){ 
  mostcommented = `${window.location.href.replace('filter=likes', 'filter=comment')}` 
}else{
  mostcommented = `${window.location.href}${window.location.href.includes('?')?'&':'?'}filter=comment`
}
let searchParams = new URLSearchParams(window.location.search)
if (searchParams.get('filter')) {
  document.querySelector(`#${searchParams.get('filter')}`).classList.replace('btn-secondary', 'btn-primary')
}else{
  document.querySelector(`#recent`).classList.replace('btn-secondary', 'btn-primary')
}
console.log(mostrecent, mostcommented, mostliked)
document.getElementById('recent').addEventListener('click', ()=>window.location.href = mostrecent)
document.getElementById('comment').addEventListener('click', ()=>window.location.href = mostcommented)
document.getElementById('likes').addEventListener('click', ()=>window.location.href = mostliked)