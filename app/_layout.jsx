import { Stack } from 'expo-router/stack';

export default function Layout() {
  return (
    <Stack
        screenOptions={{
            headerShown: false
        }}
    />
  )
}import { Stack } from "expo-router";

export default function Layout() {
  return <Stack screenOptions={{ headerShown: false }} />;
}