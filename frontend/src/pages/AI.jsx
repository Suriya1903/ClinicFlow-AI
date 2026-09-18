import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function AI() {
  const navigate = useNavigate();

  const [messages, setMessages] =
    useState([
      {
        id: 1,
        role: "assistant",
        content:
          "Hello! I'm ClinicFlow AI. I can help you understand your clinic's operational information, such as patients and appointments.",
      },
    ]);

  const [input, setInput] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const messagesEndRef =
    useRef(null);


  /* ==========================================================
     AUTO SCROLL
     ========================================================== */

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);


  /* ==========================================================
     SEND MESSAGE
     ========================================================== */

  const sendMessage = async (
    event
  ) => {
    event?.preventDefault();

    const message =
      input.trim();

    if (
      !message ||
      loading
    ) {
      return;
    }


    setError("");


    const userMessage = {
      id:
        Date.now(),
      role: "user",
      content:
        message,
    };


    setMessages(
      (previous) => [
        ...previous,
        userMessage,
      ]
    );


    setInput("");
    setLoading(true);


    try {
      const response =
        await apiClient.post(
          "/ai/agent",
          {
            message,
          }
        );


      const assistantMessage = {
        id:
          Date.now() + 1,
        role: "assistant",
        content:
          response.data?.response ||
          "I couldn't generate a response.",
      };


      setMessages(
        (previous) => [
          ...previous,
          assistantMessage,
        ]
      );

    } catch (err) {
      console.error(
        "AI Assistant error:",
        err
      );


      if (
        err.response?.status === 401
      ) {
        navigate("/login");
        return;
      }


      const detail =
        err.response?.data?.detail;


      if (
        typeof detail === "string"
      ) {
        setError(detail);
      } else {
        setError(
          "The AI assistant is currently unavailable."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  /* ==========================================================
     QUICK QUESTIONS
     ========================================================== */

  const quickQuestions = [
    "How many active patients do we have?",

    "What appointments do we have today?",

    "Give me today's clinic summary.",
  ];


  const askQuickQuestion = (
    question
  ) => {
    setInput(question);
  };


  /* ==========================================================
     CLEAR CHAT
     ========================================================== */

  const clearChat = () => {
    setMessages([
      {
        id: Date.now(),
        role: "assistant",
        content:
          "Chat cleared. How can I help you with your clinic operations?",
      },
    ]);

    setError("");
  };


  /* ==========================================================
     RENDER
     ========================================================== */

  return (
    <div className="page ai-page">

      {/* ====================================================
          HEADER
          ==================================================== */}

      <div className="page-heading">

        <div>

          <h2>
            AI Assistant
          </h2>

          <p>
            Ask ClinicFlow AI about your clinic operations.
          </p>

        </div>


        <button
          className="secondary-button"
          onClick={
            clearChat
          }
          disabled={
            loading
          }
        >
          Clear Chat
        </button>

      </div>


      {/* ====================================================
          AI NOTICE
          ==================================================== */}

      <div className="ai-notice">

        <div className="ai-notice-icon">
          AI
        </div>

        <div>

          <strong>
            ClinicFlow Operations Assistant
          </strong>

          <p>
            Responses are based on operational information from your authenticated clinic.
            This assistant is not a medical diagnosis or treatment system.
          </p>

        </div>

      </div>


      {/* ====================================================
          CHAT CARD
          ==================================================== */}

      <div className="ai-chat-card">

        {/* ================================================
            CHAT MESSAGES
            ================================================ */}

        <div className="ai-messages">

          {messages.map(
            (message) => (

              <div
                key={
                  message.id
                }
                className={
                  message.role ===
                  "user"
                    ? "ai-message-row user"
                    : "ai-message-row assistant"
                }
              >

                {message.role ===
                  "assistant" && (

                  <div className="ai-message-avatar">
                    AI
                  </div>

                )}


                <div
                  className={
                    message.role ===
                    "user"
                      ? "ai-message user"
                      : "ai-message assistant"
                  }
                >

                  <div className="ai-message-label">

                    {message.role ===
                    "user"
                      ? "You"
                      : "ClinicFlow AI"}

                  </div>


                  <div className="ai-message-content">
                    {message.content}
                  </div>

                </div>


                {message.role ===
                  "user" && (

                  <div className="ai-user-avatar">
                    U
                  </div>

                )}

              </div>

            )
          )}


          {/* ==============================================
              TYPING / LOADING
              ============================================== */}

          {loading && (

            <div className="ai-message-row assistant">

              <div className="ai-message-avatar">
                AI
              </div>


              <div className="ai-message assistant">

                <div className="ai-message-label">
                  ClinicFlow AI
                </div>


                <div className="ai-thinking">

                  <span></span>
                  <span></span>
                  <span></span>

                  <span className="ai-thinking-text">
                    Thinking...
                  </span>

                </div>

              </div>

            </div>

          )}


          <div
            ref={
              messagesEndRef
            }
          />

        </div>


        {/* ================================================
            ERROR
            ================================================ */}

        {error && (

          <div className="ai-error">
            {error}
          </div>

        )}


        {/* ================================================
            QUICK QUESTIONS
            ================================================ */}

        <div className="ai-quick-section">

          <span>
            Quick questions
          </span>


          <div className="ai-quick-buttons">

            {quickQuestions.map(
              (question) => (

                <button
                  key={
                    question
                  }
                  type="button"
                  onClick={() =>
                    askQuickQuestion(
                      question
                    )
                  }
                  disabled={
                    loading
                  }
                >
                  {question}
                </button>

              )
            )}

          </div>

        </div>


        {/* ================================================
            INPUT
            ================================================ */}

        <form
          className="ai-input-area"
          onSubmit={
            sendMessage
          }
        >

          <textarea
            value={
              input
            }
            onChange={(event) =>
              setInput(
                event.target.value
              )
            }
            onKeyDown={(event) => {

              if (
                event.key ===
                  "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();

                sendMessage(
                  event
                );
              }

            }}
            placeholder="Ask about patients, appointments, or clinic operations..."
            rows="2"
            maxLength={4000}
            disabled={
              loading
            }
          />


          <button
            type="submit"
            className="primary-button ai-send-button"
            disabled={
              loading ||
              !input.trim()
            }
          >
            {loading
              ? "Sending..."
              : "Send"}
          </button>

        </form>


        <div className="ai-input-hint">
          Press Enter to send · Shift + Enter for a new line
        </div>

      </div>

    </div>
  );
}


export default AI;