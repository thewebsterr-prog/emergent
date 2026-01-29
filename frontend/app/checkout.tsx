import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useCartStore } from '../store/cartStore';
import { getCart, createOrder, getProduct } from '../utils/api';

export default function CheckoutScreen() {
  const router = useRouter();
  const { items, clearCart } = useCartStore();
  
  const [cartItems, setCartItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  const [fullName, setFullName] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [phone, setPhone] = useState('');

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      setLoading(true);
      const cart = await getCart();
      
      const itemsWithDetails = await Promise.all(
        (cart.items || []).map(async (item: any) => {
          try {
            const product = await getProduct(item.productId);
            return {
              productId: product.id,
              name: product.name,
              price: product.price,
              quantity: item.quantity,
              image: product.image,
            };
          } catch (error) {
            return null;
          }
        })
      );
      
      setCartItems(itemsWithDetails.filter(Boolean));
    } catch (error) {
      console.error('Error loading cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + item.price * item.quantity, 0);
  };

  const handlePlaceOrder = async () => {
    if (!fullName.trim() || !address.trim() || !city.trim() || !state.trim() || !zipCode.trim() || !phone.trim()) {
      Alert.alert('Error', 'Please fill in all shipping details');
      return;
    }

    if (cartItems.length === 0) {
      Alert.alert('Error', 'Your cart is empty');
      return;
    }

    try {
      setSubmitting(true);
      
      const order = await createOrder({
        items: cartItems,
        total: calculateTotal(),
        shippingAddress: {
          fullName,
          address,
          city,
          state,
          zipCode,
          phone,
        },
      });

      clearCart();
      
      Alert.alert(
        'Order Placed!',
        'Your order has been placed successfully!',
        [
          {
            text: 'View Order',
            onPress: () => router.replace(`/order/${order.id}`),
          },
        ]
      );
    } catch (error) {
      console.error('Error placing order:', error);
      Alert.alert('Error', 'Failed to place order. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#FF6B35" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Order Summary</Text>
            {cartItems.map((item, index) => (
              <View key={index} style={styles.orderItem}>
                <Text style={styles.orderItemName}>
                  {item.name} x {item.quantity}
                </Text>
                <Text style={styles.orderItemPrice}>
                  ${(item.price * item.quantity).toFixed(2)}
                </Text>
              </View>
            ))}
            <View style={styles.totalRow}>
              <Text style={styles.totalLabel}>Total:</Text>
              <Text style={styles.totalAmount}>${calculateTotal().toFixed(2)}</Text>
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Shipping Information</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Full Name</Text>
              <TextInput
                style={styles.input}
                value={fullName}
                onChangeText={setFullName}
                placeholder="John Doe"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Address</Text>
              <TextInput
                style={styles.input}
                value={address}
                onChangeText={setAddress}
                placeholder="123 Main St"
              />
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, styles.inputHalf]}>
                <Text style={styles.inputLabel}>City</Text>
                <TextInput
                  style={styles.input}
                  value={city}
                  onChangeText={setCity}
                  placeholder="New York"
                />
              </View>

              <View style={[styles.inputGroup, styles.inputHalf]}>
                <Text style={styles.inputLabel}>State</Text>
                <TextInput
                  style={styles.input}
                  value={state}
                  onChangeText={setState}
                  placeholder="NY"
                />
              </View>
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, styles.inputHalf]}>
                <Text style={styles.inputLabel}>ZIP Code</Text>
                <TextInput
                  style={styles.input}
                  value={zipCode}
                  onChangeText={setZipCode}
                  placeholder="10001"
                  keyboardType="numeric"
                />
              </View>

              <View style={[styles.inputGroup, styles.inputHalf]}>
                <Text style={styles.inputLabel}>Phone</Text>
                <TextInput
                  style={styles.input}
                  value={phone}
                  onChangeText={setPhone}
                  placeholder="555-1234"
                  keyboardType="phone-pad"
                />
              </View>
            </View>
          </View>
        </ScrollView>

        <View style={styles.footer}>
          <TouchableOpacity
            style={[styles.placeOrderButton, submitting && styles.placeOrderButtonDisabled]}
            onPress={handlePlaceOrder}
            disabled={submitting}
          >
            {submitting ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <>
                <Ionicons name="checkmark-circle" size={20} color="#FFF" />
                <Text style={styles.placeOrderText}>Place Order</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 16,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  orderItemName: {
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  orderItemPrice: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 16,
    marginTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },
  totalAmount: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FF6B35',
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#333',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  inputHalf: {
    width: '48%',
  },
  footer: {
    backgroundColor: '#FFF',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  placeOrderButton: {
    backgroundColor: '#FF6B35',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 16,
    borderRadius: 12,
  },
  placeOrderButtonDisabled: {
    opacity: 0.6,
  },
  placeOrderText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 8,
  },
});