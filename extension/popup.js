chrome.tabs.query(
    {
        active: true,
        currentWindow: true
    },

    function (tabs) {

        const tab = tabs[0];

        document.getElementById(
            "info"
        ).innerHTML = `
            <p><b>Title:</b> ${tab.title}</p>
            <p><b>URL:</b> ${tab.url}</p>
        `;
    }
);