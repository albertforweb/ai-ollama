async function sendChat() {
  let userInput = document.getElementById("userInput").value.trim();
  if (!userInput) return; // Don't send empty messages

  // Add user's message to the chat area
  appendMessage(userInput, 'user-message');

  // Clear input after sending
  document.getElementById("userInput").value = '';

  try {
    // Start the POST request to send the message
    const response = await fetch('/api/v1/activitygpt/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: userInput })
    });

    let reader = response.body.getReader();
    let decoder = new TextDecoder();

    // Create a container for the bot's message
    let botMessageContainer = createMessageContainer('bot-message');
    
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      let chunk = decoder.decode(value, { stream: true });
      console.log(chunk);
    

      // Replace newline characters with HTML <br> tags
      chunk = chunk.replace(/\n/g, '<br>');
      botMessageContainer.innerHTML += chunk;

    }
    // Scroll the bot's message container into view
    botMessageContainer.scrollIntoView({ behavior: 'smooth' });



    // also append diagram if possible
    // appendDiagram(received);
  } catch (error) {
    console.error('Error:', error);
  }
}

async function createDiagram() {
  let userInput = document.getElementById("userInput").value.trim();

  const response =  await fetch('/api/v1/activitygpt/chatdiagram', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: userInput })
  });

  let reader = response.body.getReader();
  await reader.read().then(({ value, done }) => {
    console.log(value);
    let decoder = new TextDecoder();
    let chunk = decoder.decode(value);
    // chunk = chunk.replace(/"/g, '\\"');
    // if (chunk.includes('\\n')) {
    //   chunk = chunk.replace(/\n/g, '<br>');
    // }
    let received = chunk;
    console.log(received);
    // also append diagram if possible
    appendDiagram(received);
   });
  
   document.getElementById("userInput").value = '';
}

function appendMessage(text, className) {
  let messageContainer = createMessageContainer(className);
  messageContainer.innerHTML = text.replace(/\n/g, '<br>'); // Replace newlines with <br>
  document.getElementById('chatArea').appendChild(messageContainer);
  messageContainer.scrollIntoView({ behavior: 'smooth' });
}

function createMessageContainer(className) {
  let div = document.createElement('div');
  div.classList.add('message', className);
  document.getElementById('chatArea').appendChild(div);
  return div;
}

function appendDiagram(data) {
  console.log('raw data :', data);

  let code = `
  ${data}
  `;
  if (data.includes('\\n')) { 
    code = data.replace(/\\n/g, "\n");
  }
  console.log('code :', code);
  const diagramContainer = document.getElementsByClassName('activity-container')[0];
  // remove childrens
  while (diagramContainer.firstChild) {
    diagramContainer.removeChild(diagramContainer.firstChild);
  }
  let pre = document.createElement('pre');
  pre.className = 'mermaid';
  pre.textContent = code;
  diagramContainer.appendChild(pre);
  mermaid.init(undefined, pre);
}

// DOM ready
document.addEventListener("DOMContentLoaded", () => {

  // show sample diagram
  const diagramContainer = document.getElementsByClassName('activity-container')[0];
  
  let mermaidCode = `
flowchart LR
    subgraph G1["CDNA"]
      A[kong] -->|logs| B(activity gpt agent)
      B -->|vectors| C[(Qdrant DB)]
      D[UI] -->|question| B
    end
    U[user] -->|question| D
    subgraph G2["AWS"]
      E[Bedrock LLM]
    end
    
    B -->|chat| E
  `;
 
  let pre = document.createElement('pre');
  pre.className = 'mermaid';
  pre.innerHTML = mermaidCode
  diagramContainer.appendChild(pre);

  mermaid.init(undefined, pre);
});