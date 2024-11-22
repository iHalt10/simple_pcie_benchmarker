# https://www.info.kindai.ac.jp/OS/reference/buddySystem.pdf
# https://zenn.dev/junjunjunjun/articles/6e6ed31167b0ca
class BuddyAllocator:
    def __init__(self, size: int, min_alloc: int = 1):
        if size <= 0 or (size & (size - 1)) != 0:
            raise ValueError("'size' must be a power of 2")
        if min_alloc <= 0 or (min_alloc & (min_alloc - 1)) != 0:
            raise ValueError("'min_alloc' must be a power of 2")

        self._size = size
        self._min_alloc = min_alloc
        self._max_order = self._get_order(size)
        self._free_lists: list[list[int]] = [[] for _ in range(self._max_order + 1)]
        self._free_lists[self._max_order].append(0)  # NOTE: Initially all memory is free
        self._allocated: dict[int, int] = {}  # NOTE: key: value = addr: order

    def _get_order(self, size: int) -> int:
        return (size - 1).bit_length()

    def _split_block(self, addr: int, current_order: int, required_order: int) -> None:
        while current_order > required_order:
            current_order -= 1
            buddy_addr = addr + (1 << current_order)
            self._free_lists[current_order].append(buddy_addr)

    def alloc(self, size: int) -> int:
        required_order = self._get_order(max(size, self._min_alloc))

        for current_order in range(required_order, self._max_order + 1):
            if self._free_lists[current_order]:
                addr = self._free_lists[current_order].pop(0)
                self._split_block(addr, current_order, required_order)
                self._allocated[addr] = required_order
                return addr

        raise MemoryError("Out of memory")

    def _merge_block(self, addr: int, order: int) -> None:
        while order < self._max_order:
            buddy_addr = addr ^ (1 << order)

            if buddy_addr in self._free_lists[order]:
                self._free_lists[order].remove(buddy_addr)
                addr = min(addr, buddy_addr)
                order += 1
            else:
                break

        self._free_lists[order].append(addr)

    def free(self, addr: int) -> None:
        if addr not in self._allocated:
            raise MemoryError(f"Unknown allocation: {addr}")

        order = self._allocated.pop(addr)
        self._merge_block(addr, order)

    def display_memory(self) -> None:
        memory_map: list[str] = []
        total_size = self._size
        used_blocks = sorted(self._allocated.items())

        current_addr = 0
        used_idx = 0

        while current_addr < total_size:
            if used_idx < len(used_blocks) and used_blocks[used_idx][0] == current_addr:
                block_size = 1 << used_blocks[used_idx][1]
                memory_map.append(f"*{block_size}")
                current_addr += block_size
                used_idx += 1
            else:
                for order in range(self._max_order, -1, -1):
                    block_size = 1 << order
                    if current_addr in self._free_lists[order]:
                        memory_map.append(f"{block_size}")
                        current_addr += block_size
                        break

        print("|".join(memory_map))


def test_buddy_allocator():
    allocator = BuddyAllocator(1024, 64)
    addr_100 = allocator.alloc(100)
    allocator.display_memory()
    addr_240 = allocator.alloc(240)
    allocator.display_memory()
    addr_60 = allocator.alloc(60)
    allocator.display_memory()
    addr_200 = allocator.alloc(200)
    allocator.display_memory()
    allocator.free(addr_240)
    allocator.display_memory()
    allocator.free(addr_100)
    allocator.display_memory()
    addr_70 = allocator.alloc(70)
    allocator.display_memory()
    allocator.free(addr_60)
    allocator.display_memory()
    allocator.free(addr_70)
    allocator.display_memory()
    allocator.free(addr_200)
    allocator.display_memory()
