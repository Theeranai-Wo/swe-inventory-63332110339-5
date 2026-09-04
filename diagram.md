# Class Diagram: ระบบขาย RAM

```mermaid
classDiagram

class User {
    +userId: String
    +name: String
    +email: String
    +role: UserRole
}

class Product {
    +productId: String
    +name: String
    +brand: String
    +price: Decimal
    +stockQty: int
    +category: String
}

class RAM {
    +capacityGB: int
    +speedMHz: int
    +ramType: String
    +hasRGB: bool
    +rgbSync: String
    +packageType: PackageType
    +moduleCount: int
    +timing: String
    +voltage: Decimal
    +memoryChip: String
}

class RGBSync {
    +syncName: String
    +supportedBrand: String
}

class Filter {
    +brand: String
    +rgbSync: String
    +minCapacityGB: int
    +packageType: PackageType
    +apply()
}

class Sale {
    +saleId: String
    +saleDate: DateTime
    +totalAmount: Decimal
    +confirmSale()
}

class SaleItem {
    +quantity: int
    +unitPrice: Decimal
    +subtotal: Decimal
}

class SerialNumber {
    +serialNo: String
    +status: SerialStatus
    +scan()
}

class Inventory {
    +inventoryId: String
    +stockQty: int
    +deductStock()
    +increaseStock()
    +getStockQty()
}

class Chat {
    +chatId: String
    +createdAt: DateTime
    +status: ChatStatus
    +sendMessage()
    +notifyStaff()
}

class Message {
    +messageId: String
    +content: String
    +sentAt: DateTime
    +messageType: MessageType
}

class Image {
    +imageId: String
    +fileName: String
    +fileUrl: String
    +uploadedAt: DateTime
}

class Staff {
    +staffId: String
    +name: String
    +onlineStatus: bool
    +receiveNotification()
    +replyChat()
}

class AdvancedTechSpec {
    +timing: String
    +voltage: Decimal
    +memoryChip: String
    +showDetails()
}

class UserRole {
    <<enumeration>>
    CUSTOMER
    STAFF
    ADMIN
}

class PackageType {
    <<enumeration>>
    SINGLE
    KIT_2
    KIT_4
}

class SerialStatus {
    <<enumeration>>
    IN_STOCK
    SOLD
}

class ChatStatus {
    <<enumeration>>
    WAITING
    ACTIVE
    CLOSED
}

class MessageType {
    <<enumeration>>
    TEXT
    IMAGE
}

User "1" --> "0..*" Sale : makes
User "1" --> "0..*" Chat : starts
User "1" --> "0..*" Filter : uses

Product <|-- RAM

RAM "1" --> "0..*" RGBSync : supports
RAM "1" --> "1" AdvancedTechSpec : has
RAM "1" --> "1" Inventory : tracked by
RAM "1" --> "1..*" SerialNumber : identified by

Filter --> RAM : filters

Sale "1" *-- "1..*" SaleItem : contains
SaleItem "*" --> "1" RAM : sold RAM
SaleItem "1" --> "1" SerialNumber : uses

Inventory --> RAM : manages

Chat "1" *-- "1..*" Message : contains
Message "0..*" --> "0..*" Image : attaches

Chat "*" --> "0..1" Staff : handled by
Staff "1" --> "0..*" Chat : handles
