-worker.js
self.addEventListener('install', function(event) {
  self.skipWaiting();
});
self.addEventListener('fetch', function(event) {
  // You can add caching logic here if desired
});
