import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="product/[id]" options={{ presentation: 'card', headerShown: true, title: 'Product Details' }} />
        <Stack.Screen name="checkout" options={{ presentation: 'card', headerShown: true, title: 'Checkout' }} />
        <Stack.Screen name="order/[id]" options={{ presentation: 'card', headerShown: true, title: 'Order Details' }} />
      </Stack>
    </SafeAreaProvider>
  );
}