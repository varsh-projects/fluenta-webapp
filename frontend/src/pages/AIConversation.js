import React, { useState } from "react";

function AIConversation() {

  const [speech, setSpeech] = useState("");
  const [reply, setReply] = useState("");
  const [score, setScore] = useState(null);

  const speakAI = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    speechSynthesis.speak(utterance);
  };

  const startListening = () => {

    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech recognition not supported");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;

    recognition.onresult = async (event) => {

      const text = event.results[0][0].transcript;

      setSpeech(text);

      const response = await fetch("http://127.0.0.1:8000/conversation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
      });

      const data = await response.json();

      setReply(data.reply);
      setScore(data.score);

      speakAI(data.reply);   // AI talks back
    };

    recognition.start();
  };

  return (

    <div style={{ padding: "40px", fontFamily: "Arial" }}>

      <h1>Fluenta AI Conversation</h1>

      <button onClick={startListening}>
        🎤 Speak
      </button>

      <h3>Your Speech</h3>
      <p>{speech}</p>

      <h3>AI Reply</h3>
      <p>{reply}</p>

      <h3>Scores</h3>

      {score && (
        <div>
          <p>Fluency: {score.fluency}</p>
          <p>Grammar: {score.grammar}</p>
          <p>Pronunciation: {score.pronunciation}</p>
          <p>Vocabulary: {score.vocabulary}</p>
        </div>
      )}

    </div>
  );
}

export default AIConversation;