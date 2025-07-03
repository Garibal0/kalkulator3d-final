self.addEventListener('install', () => {
  console.log('Service Worker zainstalowany');
});

self.addEventListener('fetch', () => {
  // Można dodać caching w przyszłości
});
