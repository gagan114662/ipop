import { Pet, Order } from './types'

export class PetStoreService {
  private petIdCounter = 1
  private orderIdCounter = 1

  async createPet(petData: { name: string; photoUrl: string }): Promise<Pet> {
    const newPet: Pet = {
      id: this.petIdCounter++,
      name: petData.name,
      photoUrl: petData.photoUrl,
      status: 'available',
      createdAt: new Date().toISOString(),
    }
    
    console.log(`Created new pet: ${newPet.name} with ID ${newPet.id}`)
    return newPet
  }

  async createOrder(orderData: {
    email: string
    quantity: number
    petId: number
    shipDate: string
    status: string
  }): Promise<Order> {
    const newOrder: Order = {
      id: this.orderIdCounter++,
      petId: orderData.petId,
      quantity: orderData.quantity,
      shipDate: orderData.shipDate,
      status: orderData.status,
      complete: false,
      email: orderData.email,
    }
    
    console.log(`Created new order: ${newOrder.id} for pet ${newOrder.petId}`)
    return newOrder
  }
}

export const petStoreService = new PetStoreService()