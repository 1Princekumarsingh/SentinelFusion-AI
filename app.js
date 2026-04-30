//creating websocket connection
let ws = new WebSocket("ws://127.0.0.1:8000/ws/stats");

//current button state
let heatmapOn = true;
let depthOn= true;

ws.onopen = function(){
    console.log("Stats WebSocket connected");
}

ws.onerror = function(error){
    console.error("Stats WebSocket error:", error);
}

ws.onclose = function(event){
    console.warn("Stats WebSocket closed:", event.code, event.reason);
}

//web socket listener
ws.onmessage = function(event){
    let data = JSON.parse(event.data);
    let alerts = Array.isArray(data.alerts) ? data.alerts : [];

   document.getElementById('fps').innerText = data.fps ?? 0;
   document.getElementById("objects").innerText = data.objects ?? 0;

   let alertsDiv = document.getElementById("alerts");
   alertsDiv.innerHTML = "";

   alerts.forEach(alert => {
    let div = document.createElement("div");
    div.className = "alert";

    if (alert.type === "proximity"){
        div.innerText = `IDs ${alert.pair[0]} & ${alert.pair[1]} TOO CLOSE`;
    }
    alertsDiv.appendChild(div);
   })
}

// heatmap toggle
document.getElementById("heatmapBtn").onclick = async function(){
    heatmapOn = !heatmapOn
    
    await fetch(`http://127.0.0.1:8000/config?heatmap=${heatmapOn}`, 
        {method: "POST"}
    );

    this.innerText = heatmapOn? "Heatmap ON" : "Heatmap OFF";
    
    this.classList.remove("btn-on", "btn-off"); //remove the current button
    this.classList.add(heatmapOn? "btn-on" : "btn-off");
}

// depth toggle
document.getElementById("depthBtn").onclick = async function(){
    depthOn = !depthOn
    
    await fetch(`http://127.0.0.1:8000/config?depth=${depthOn}`, 
        {method: "POST"}
    );

    this.innerText = depthOn? "Depth ON" : "Depth OFF";
    
    this.classList.remove("btn-on", "btn-off"); //remove the current button
    this.classList.add(depthOn? "btn-on" : "btn-off");
}
