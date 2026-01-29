import { create } from 'zustand';

interface CartItem {
  productId: string;
  quantity: number;
}

interface CartStore {
  items: CartItem[];
  setItems: (items: CartItem[]) => void;
  addItem: (productId: string, quantity: number) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  removeItem: (productId: string) => void;
  clearCart: () => void;
  getItemCount: () => number;
}

export const useCartStore = create<CartStore>((set, get) => ({
  items: [],
  setItems: (items) => set({ items }),
  addItem: (productId, quantity) => {
    const currentItems = get().items;
    const existingItem = currentItems.find(item => item.productId === productId);
    if (existingItem) {
      set({
        items: currentItems.map(item =>
          item.productId === productId
            ? { ...item, quantity: item.quantity + quantity }
            : item
        ),
      });
    } else {
      set({ items: [...currentItems, { productId, quantity }] });
    }
  },
  updateQuantity: (productId, quantity) => {
    if (quantity <= 0) {
      set({ items: get().items.filter(item => item.productId !== productId) });
    } else {
      set({
        items: get().items.map(item =>
          item.productId === productId ? { ...item, quantity } : item
        ),
      });
    }
  },
  removeItem: (productId) => {
    set({ items: get().items.filter(item => item.productId !== productId) });
  },
  clearCart: () => set({ items: [] }),
  getItemCount: () => {
    return get().items.reduce((total, item) => total + item.quantity, 0);
  },
}));