console.log("NEW BACKGROUND VERSION LOADED");
chrome.tabs.onActivated.addListener(
    
    async function(activeInfo) {

        const tab = await chrome.tabs.get(
            activeInfo.tabId
        );
        console.log("About to send request");
        console.log("Tab Changed:");
        console.log("Title:", tab.title);
        console.log("URL:", tab.url);

        console.log("About to send request");

fetch(
    "http://127.0.0.1:5000/browser_activity",
    {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: tab.title,
            url: tab.url
        })
    }
)
.then(response => {
    console.log("Response received");
    return response.json();
})
.then(data => {
    console.log("SUCCESS:", data);
})
.catch(error => {
    console.error("FETCH ERROR:");
    console.error(error);
    console.error(error.message);
});
    }
);

chrome.tabs.onUpdated.addListener(
    function(tabId, changeInfo, tab) {

        if (changeInfo.status === "complete") {

            console.log(
                "Page Loaded:"
            );

            console.log(
                "Title:",
                tab.title
            );

            console.log(
                "URL:",
                tab.url
            );
        }
    }
);
