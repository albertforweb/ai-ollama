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
      let received = '';
      while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          let chunk = decoder.decode(value, { stream: true });
          console.log(chunk);
          received += chunk;

          // Replace newline characters with HTML <br> tags
          chunk = chunk.replace(/\n/g, '<br>');
          botMessageContainer.innerHTML += chunk;
          
      }
      // Scroll the bot's message container into view
      botMessageContainer.scrollIntoView({ behavior: 'smooth' });



      // also append diagram if possible
      appendDiagram(received);
  } catch (error) {
      console.error('Error:', error);
  }
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
  let code = data.replace("\"","");
  console.log('received data:', data);
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
  let pre = document.createElement('pre');
  pre.className = 'mermaid';
  pre.innerHTML = `
flowchart LR
    A[Hard edge] -->|Link text| B(Round edge)
    B --> C{Decision}
    C -->|One| D[Result one]
    C -->|Two| E[Result two]
  `;
  diagramContainer.appendChild(pre);
});