document.querySelector('#search-form')?.addEventListener('submit', function (event) {
  event.preventDefault();
  const artist = encodeURIComponent(this.artist.value.trim());
  const song = encodeURIComponent(this.song.value.trim());
  window.location.href = `/artists/${artist}/songs/${song}`;
});
