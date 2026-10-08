# Sprint Retrospective: Sprint 1

## Velocity
- Story point ที่วางแผน: 8
- Story point ที่ทำสำเร็จ (Done): 8
- Velocity Sprint 1: 8 points

## เพดานงานที่ทำพร้อมกัน (WIP limit)
- เพดานที่ตั้งไว้ใน TEAM_CHARTER.md: 3 ใบ
- ชนเพดานกี่ครั้งใน sprint นี้: 1 ครั้ง
- เพดานที่จะใช้ใน sprint หน้า: 3 ใบ เพราะ เหมาะสมกับจำนวนสมาชิกและช่วยให้ทุกคนช่วยกันรีวิว PR ก่อนดึงงานใหม่

## Start: สิ่งที่ควรเริ่มทำในรอบต่อไป
- เริ่มเขียน Automated Unit Test สำหรับทดสอบ `sell_by_serial` ทุก edge case
- กำหนด Template ของ PR Description ให้เพื่อนรีวิวได้ง่ายขึ้น

## Stop: สิ่งที่ควรหยุดทำ
- หยุดลืมอัปเดตสถานะการ์ดบน GitHub Projects ขณะเริ่มทำ branch
- หยุดเปิด PR ขนาดใหญ่เกินไป ให้แตกเป็นก้อนเล็ก ๆ เพื่อให้รีวิวง่าย

## Continue: สิ่งที่ทำได้ดี ควรทำต่อ
- การใช้ GitHub Flow อย่างเคร่งครัด ไม่มีใคร push ตรงเข้า main
- การตั้งชื่อ branch ตามรูปแบบ `feat/<issue-num>-<name>` ชัดเจน

## AI Commit Audit
- **PR #3:** Draft commit message จาก AI เขียนว่า `feat: update inventory` สั้นเกินไป ได้แก้เป็น `feat: เพิ่มฟังก์ชัน sell_by_serial() สำหรับตัดสต็อกตาม US-02` เพื่อให้ตรงกับ Acceptance Criteria
## Action Item สำหรับ Sprint ถัดไป
| Action | เจ้าของ |
|---|---|
| ออกแบบ Data Structure และ Interface สำหรับ US-04 (RAM Kit) และ US-05 ลงใน spec.md | (Ratchapong) |
| สร้าง Test Suite สำหรับตรวจ Edge Cases ของการตัดสต็อกก่อนเปิด PR | (Thanawat) |

<img width="1522" height="811" alt="image" src="https://github.com/user-attachments/assets/e0446124-ff26-49a9-aca4-ec4b2bf154e4" />
