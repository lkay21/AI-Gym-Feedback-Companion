import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { chatAPI } from "../services/api";
import MenuDropdown from "../components/MenuDropdown";

const BOT_NAME = "Fred";

export default function ChatBotScreen({ route }) {
  const { q } = route?.params || {};
  const listRef = useRef(null);

  const initialMessages = useMemo(
    () => [
      {
        id: "m1",
        role: "bot",
        text: `Hello! I'm ${BOT_NAME}, your AI\nFitness Companion.\n\nTell me your fitness goal or ask a question to get started.`,
        kind: "headline",
      },
    ],
    []
  );

  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const normalizeBotText = (raw) => {
    if (!raw) return "";
    let text = String(raw);
    // Normalise newlines
    text = text.replace(/\r\n/g, "\n");
    // Strip bold markdown markers **text**
    text = text.replace(/\*\*(.*?)\*\*/g, "$1");
    // Convert bullet markdown (* or -) at line start to a nicer bullet
    text = text.replace(/^[\s]*[-*]\s+/gm, "• ");
    return text.trim();
  };

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      try {
        listRef.current?.scrollToEnd({ animated: true });
      } catch {
        // ignore
      }
    });
  };

  const buildMockBotReply = (userText) => {
    const t = userText.toLowerCase();

    if (t.includes("plan") || t.includes("workout")) {
      return (
        "Got it — I'll adjust your workouts based on that.\n" +
        "Check the Fitness Dashboard to review the updated plan."
      );
    }
    if (t.includes("calorie") || t.includes("diet") || t.includes("food")) {
      return (
        "Noted. I can tailor your calorie target and meal guidance.\n" +
        "Tell me your typical day of eating and any dietary restrictions."
      );
    }
    if (t.includes("knee") || t.includes("pain") || t.includes("injur")) {
      return (
        "Thanks for sharing. I can swap exercises to reduce strain.\n" +
        "Which movements trigger discomfort most?"
      );
    }
    return (
      "Sounds good — I've saved that.\n" +
      "Want me to update your plan or answer a quick question?"
    );
  };

  const sendText = async (text) => {
    const trimmed = String(text ?? "").trim();
    if (!trimmed) return;

    const userMsg = { id: `u_${Date.now()}`, role: "user", text: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    scrollToBottom();

    setLoading(true);
    setError("");

    try {
      const history = [...messages, userMsg]
      .filter((m) => m.kind !== "intro")
      .map((m) => ({
        role: m.role,
        text: m.text,
      }));

      const result = await chatAPI.sendChatbotMessage(trimmed, history, {});

      if (!result.success) {
        setError(result.error || "Failed to reach chatbot service.");
        // Fallback to local mock reply so the UI is not dead
        const fallback = {
          id: `b_${Date.now()}`,
          role: "bot",
          text: buildMockBotReply(trimmed),
        };
        setMessages((prev) => [...prev, fallback]);
        scrollToBottom();
        return;
      }

      const responseText =
        result.data?.response ||
        result.data?.data?.response ||
        result.data?.data ||
        buildMockBotReply(trimmed);

      const botMsg = {
        id: `b_${Date.now()}`,
        role: "bot",
        text: normalizeBotText(responseText),
      };
      setMessages((prev) => [...prev, botMsg]);
      scrollToBottom();
    } catch (e) {
      setError("Something went wrong talking to the chatbot. Using a local reply.");
      const botMsg = {
        id: `b_${Date.now()}`,
        role: "bot",
        text: normalizeBotText(buildMockBotReply(trimmed)),
      };
      setMessages((prev) => [...prev, botMsg]);
      scrollToBottom();
    } finally {
      setLoading(false);
    }
  };

  const lastQRef = useRef(null);

  useEffect(() => {
    if (!q) return;

    const incoming = Array.isArray(q) ? q[0] : q;
    const trimmed = String(incoming ?? "").trim();
    if (!trimmed) return;

    if (lastQRef.current === trimmed) return;
    lastQRef.current = trimmed;

    sendText(trimmed);
  }, [q]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    setInput("");
    void sendText(trimmed);
  };

  const renderItem = ({ item }) => {
    const isUser = item.role === "user";
    const isHeadline = item.kind === "headline";

    if (isHeadline) {
      return <Text style={styles.headline}>{item.text}</Text>;
    }

    return (
      <View style={[styles.messageRow, isUser ? styles.rowRight : styles.rowLeft]}>
        <View style={[styles.bubble, isUser ? styles.userBubble : styles.botBubble]}>
          <Text style={[styles.messageText, isUser ? styles.userText : styles.botText]}>
            {item.text}
          </Text>
        </View>
      </View>
    );
  };

  return (
    <LinearGradient
      colors={["#4C76D6", "#8E5AAE"]}
      start={{ x: 0.15, y: 0.1 }}
      end={{ x: 0.85, y: 0.95 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.safe}>
        <KeyboardAvoidingView
          style={styles.safe}
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          keyboardVerticalOffset={Platform.OS === "ios" ? 8 : 0}
        >
          <View style={styles.card}>
            <View style={styles.topBar}>
              <Text style={styles.screenTitle}>ChatBot Screen</Text>
              <MenuDropdown />
            </View>

            {error ? <Text style={styles.errorText}>{error}</Text> : null}

            <FlatList
              ref={listRef}
              data={messages}
              keyExtractor={(item) => item.id}
              renderItem={renderItem}
              contentContainerStyle={styles.listContent}
              showsVerticalScrollIndicator={false}
              onContentSizeChange={scrollToBottom}
            />

            <View style={styles.inputWrap}>
              <View style={styles.inputPill}>
                <TextInput
                  value={input}
                  onChangeText={setInput}
                  placeholder="Enter Your Prompt Here..."
                  placeholderTextColor="rgba(0,0,0,0.45)"
                  style={styles.input}
                  returnKeyType="send"
                  onSubmitEditing={handleSend}
                />
                <Pressable onPress={handleSend} style={styles.sendBtn}>
                  <Ionicons
                    name={loading ? "hourglass" : "arrow-up"}
                    size={18}
                    color="#fff"
                  />
                </Pressable>
              </View>
            </View>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },

  card: {
    flex: 1,
    marginHorizontal: 16,
    marginTop: 10,
    marginBottom: 14,
    borderRadius: 28,
    paddingTop: 12,
    paddingHorizontal: 14,
    backgroundColor: "rgba(255,255,255,0.14)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
    overflow: "hidden",
  },

  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 6,
    paddingBottom: 10,
  },

  errorText: {
    color: "#fecaca",
    fontSize: 12,
    marginHorizontal: 6,
    marginBottom: 4,
  },
  screenTitle: {
    color: "rgba(255,255,255,0.8)",
    fontSize: 14,
    letterSpacing: 0.2,
  },

  listContent: {
    paddingHorizontal: 4,
    paddingBottom: 10,
  },

  headline: {
    color: "white",
    fontSize: 24,
    fontWeight: "700",
    lineHeight: 30,
    paddingHorizontal: 6,
    paddingBottom: 14,
  },

  messageRow: {
    width: "100%",
    marginVertical: 6,
    flexDirection: "row",
  },
  rowLeft: { justifyContent: "flex-start" },
  rowRight: { justifyContent: "flex-end" },

  bubble: {
    maxWidth: "82%",
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 16,
  },
  botBubble: {
    backgroundColor: "rgba(255,255,255,0.12)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.16)",
    borderTopLeftRadius: 8,
  },
  userBubble: {
    backgroundColor: "rgba(255,255,255,0.22)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.18)",
    borderTopRightRadius: 8,
  },

  messageText: {
    fontSize: 12.5,
    lineHeight: 17,
  },
  botText: { color: "rgba(255,255,255,0.95)" },
  userText: { color: "rgba(255,255,255,0.98)" },

  inputWrap: {
    paddingTop: 10,
    paddingBottom: 14,
    paddingHorizontal: 2,
  },
  inputPill: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(255,255,255,0.95)",
    borderRadius: 999,
    paddingLeft: 16,
    paddingRight: 10,
    height: 54,
  },
  input: {
    flex: 1,
    fontSize: 14,
    color: "#111",
    paddingRight: 10,
  },
  sendBtn: {
    width: 38,
    height: 38,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#6D5ACF",
  },
});
