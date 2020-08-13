class GroupHelper:
    @staticmethod
    def group_by_range(start, end, gap):
        """
        适用于连续数值范围，如 pk range，每个worker每次处理gap量的数据
        :return: [[seg_start, seg_end], ...]
        """
        flag = start
        result = []
        while flag < end:
            result.append([flag, flag + gap])
            flag += gap
        return result

    @staticmethod
    def group_by_items(iter_items, gap: int):
        """
        适用于确切值分组，如 文件名 的集合，每个worker每次处理gap量的文件
        :return: [[item1, item2, ...], [itemx, itemy, ...], ...]
        """
        result = []
        count = 0
        tmp = []
        for item in iter_items:
            if count >= gap:
                result.append(tmp)
                count = 0
                tmp = []

            count += 1
            tmp.append(item)

        if tmp:
            result.append(tmp)
        return result
