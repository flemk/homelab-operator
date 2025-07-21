function isMobileDevice() {
    return /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function screenWidth() {
    return window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
}

function applyMobileStyles() {
    if (isMobileDevice() || screenWidth() <= 970) {
        document.querySelector('html').classList.add('mobile');
    } else {
        document.querySelector('html').classList.remove('mobile');
    }
}

window.addEventListener('resize', function() {
    applyMobileStyles();
});
applyMobileStyles();
