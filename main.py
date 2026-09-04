from inventory import InventoryService, NotifierFactory

def main():
    # สร้าง Notifier ด้วย Factory Pattern และส่งเข้า Service (DIP + Observer)
    console_observer = NotifierFactory.create("console")
    log_observer = NotifierFactory.create("log")
    
    inv_service = InventoryService(observers=[console_observer, log_observer])

    while True:
        print("\n==========================================")
        print("   ระบบสต็อกและค้นหา RAM (Computer Shop)   ")
        print("==========================================")
        print("1. ค้นหา RAM ตามเงื่อนไข RGB / Sync (US-01)")
        print("2. ขายหน้าร้านด้วย Serial Number + ตรวจสอบสต็อกต่ำ (US-02)")
        print("3. ส่งรูปภาพปรึกษาผู้เชี่ยวชาญ (US-03)")
        print("4. กรอง RAM แบบ Kit ความจุ 64GB ขึ้นไป (US-04)")
        print("5. ดูสเปกเชิงลึก Advanced Tech Specs (US-05)")
        print("0. ออกจากโปรแกรม")
        choice = input("เลือกเมนู: ").strip()

        if choice == "1":
            rgb_in = input("ต้องการไฟ RGB หรือไม่? (y/n): ").strip().lower() == 'y'
            sync_in = input("ระบุระบบ Sync (เช่น ASUS Aura Sync, กด Enter ถ้าไม่ระบุ): ").strip()
            items = inv_service.filter_ram(require_rgb=rgb_in, sync_system=sync_in if sync_in else None)
            if not items:
                print(">> ไม่พบสินค้าที่ตรงกับเงื่อนไข")
            else:
                for idx, it in enumerate(items, 1):
                    print(f"{idx}. {it['productName']} | Sync: {', '.join(it['rgbSyncSystems'])} | คงเหลือ: {it['stockQuantity']}")

        elif choice == "2":
            sn = input("สแกน/กรอก Serial Number: ").strip()
            success, msg, alert = inv_service.sell_by_serial(sn)
            print(f">> ผลการทำงาน: {msg}")

        elif choice == "3":
            uid = input("User ID ของคุณ: ").strip()
            img = input("ระบุชื่อไฟล์รูปภาพ: ").strip()
            online = input("จำลองสถานะมีพนักงานออนไลน์หรือไม่? (y/n): ").strip().lower() == 'y'
            _, res = inv_service.submit_chat_request(uid, img, staff_online=online)
            print(f">> {res}")

        elif choice == "4":
            items = inv_service.filter_ram(package_type="KIT", min_capacity=64)
            if not items:
                print(">> ไม่พบ RAM แบบ Kit ที่มีความจุ 64GB ขึ้นไป")
            else:
                for idx, it in enumerate(items, 1):
                    print(f"{idx}. {it['productName']} ({it['capacity']}GB Kit) | คงเหลือ: {it['stockQuantity']}")

        elif choice == "5":
            items = inv_service.filter_ram()
            for idx, it in enumerate(items, 1):
                print(f"[{idx}] {it['productName']}")
            sel = input("เลือกลำดับสินค้า: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(items):
                target = items[int(sel) - 1]
                print(f"\n--- Advanced Tech Specs: {target['productName']} ---")
                print(f"Timing      : {target.get('timing') or 'ไม่มีข้อมูล'}")
                print(f"Voltage     : {target.get('voltage') or 'ไม่มีข้อมูล'}")
                print(f"Memory Chip : {target.get('memoryChipManufacturer') or 'ไม่มีข้อมูล'} {target.get('memoryChipType') or ''}".strip() or 'ไม่มีข้อมูล')

        elif choice == "0":
            break

if __name__ == "__main__":
    main()
