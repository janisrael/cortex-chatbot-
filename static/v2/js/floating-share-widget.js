// Floating Share Widget JavaScript
// Handles social media sharing functionality

/**
 * Get current page URL and title for sharing
 */
function getShareData() {
    const url = window.location.href;
    const title = document.title || 'Cortex AI';
    return { url, title };
}

/**
 * Share on Facebook
 */
function shareOnFacebook(event) {
    event.preventDefault();
    const { url } = getShareData();
    const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(shareUrl, 'facebook-share-dialog', 'width=626,height=436');
}

/**
 * Share on LinkedIn
 */
function shareOnLinkedIn(event) {
    event.preventDefault();
    const { url } = getShareData();
    const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
    window.open(shareUrl, 'linkedin-share-dialog', 'width=626,height=436');
}

/**
 * Share on Twitter
 */
function shareOnTwitter(event) {
    event.preventDefault();
    const { url, title } = getShareData();
    const text = `Check out ${title}`;
    const shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
    window.open(shareUrl, 'twitter-share-dialog', 'width=626,height=436');
}

/**
 * Share on Instagram
 * Note: Instagram doesn't support direct URL sharing via web
 * This will open Instagram in a new tab
 */
function shareOnInstagram(event) {
    event.preventDefault();
    // Instagram doesn't support direct URL sharing via web API
    // Open Instagram website instead
    window.open('https://www.instagram.com', '_blank');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Floating share widget initialized');
});

