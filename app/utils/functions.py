from typing import List, Dict, Optional


class Functions:
    @staticmethod
    def process_amount_data_for_echarts(data: List) -> Dict:
        # 第一层：按部门汇总
        department_summary = {}
        for item in data:
            admin_unit_name = item.ADMIN_UNIT_NAME or ""
            amount = item.AMOUNT or 0
            price_qty = getattr(item, 'PRICE_QTY', 0) or 0
            if admin_unit_name not in department_summary:
                department_summary[admin_unit_name] = {
                    'name': admin_unit_name,
                    'value': amount,
                    'quantity': price_qty,
                    'group_id': '销售团队',
                    'child_group_id': f'销售团队 {admin_unit_name}'
                }
            else:
                department_summary[admin_unit_name]['value'] += amount
                department_summary[admin_unit_name]['quantity'] += price_qty

        # 第二层：按部门和业务员汇总
        employee_summary = {}
        employee_values = {}  # 用于汇总相同员工的销售额
        employee_quantities = {}  # 用于汇总相同员工的数量
        
        for item in data:
            admin_unit_name = item.ADMIN_UNIT_NAME or ""
            employee_name = item.EMPLOYEE_NAME or ""
            amount = item.AMOUNT or 0
            price_qty = getattr(item, 'PRICE_QTY', 0) or 0
            key = f'销售团队 {admin_unit_name}'
            
            # 创建唯一标识
            emp_key = f"{key} {employee_name}"
            
            if key not in employee_summary:
                employee_summary[key] = []
                employee_values[key] = {}
                employee_quantities[key] = {}
                
            # 如果该员工已存在，则累加金额和数量
            if employee_name in employee_values[key]:
                employee_values[key][employee_name] += amount
                employee_quantities[key][employee_name] += price_qty
            else:
                employee_values[key][employee_name] = amount
                employee_quantities[key][employee_name] = price_qty
        
        # 将汇总后的员工数据添加到结果中
        for dept_key, emp_dict in employee_values.items():
            for emp_name, emp_value in emp_dict.items():
                employee_summary[dept_key].append({
                    'name': emp_name,
                    'value': emp_value,
                    'quantity': employee_quantities[dept_key][emp_name],
                    'group_id': dept_key,
                    'child_group_id': f'{dept_key} {emp_name}'
                })

        # 第三层：按业务员和产品类别汇总
        shortcut_summary = {}
        shortcut_values = {}  # 用于汇总相同产品类别的销售额
        shortcut_quantities = {}  # 用于汇总相同产品类别的数量
        
        for item in data:
            admin_unit_name = item.ADMIN_UNIT_NAME or ""
            employee_name = item.EMPLOYEE_NAME or ""
            shortcut = item.SHORTCUT or ""
            amount = item.AMOUNT or 0
            price_qty = getattr(item, 'PRICE_QTY', 0) or 0
            key = f'销售团队 {admin_unit_name} {employee_name}'
            
            # 创建唯一标识
            shortcut_key = f"{key} {shortcut}"
            
            if key not in shortcut_summary:
                shortcut_summary[key] = []
                shortcut_values[key] = {}
                shortcut_quantities[key] = {}
                
            # 如果该产品类别已存在，则累加金额和数量
            if shortcut in shortcut_values[key]:
                shortcut_values[key][shortcut] += amount
                shortcut_quantities[key][shortcut] += price_qty
            else:
                shortcut_values[key][shortcut] = amount
                shortcut_quantities[key][shortcut] = price_qty
        
        # 将汇总后的产品类别数据添加到结果中
        for emp_key, shortcut_dict in shortcut_values.items():
            for shortcut_name, shortcut_value in shortcut_dict.items():
                shortcut_summary[emp_key].append({
                    'name': shortcut_name,
                    'value': shortcut_value,
                    'quantity': shortcut_quantities[emp_key][shortcut_name],
                    'group_id': emp_key,
                    'child_group_id': f'{emp_key} {shortcut_name}'
                })

        # 第四层：按产品类别和产品编码汇总
        item_code_summary = {}
        item_code_values = {}  # 用于汇总相同产品编码的销售额
        item_code_quantities = {}  # 用于汇总相同产品编码的数量
        
        for item in data:
            admin_unit_name = item.ADMIN_UNIT_NAME or ""
            employee_name = item.EMPLOYEE_NAME or ""
            shortcut = item.SHORTCUT or ""
            item_name = item.ITEM_NAME or ""
            amount = item.AMOUNT or 0
            price_qty = getattr(item, 'PRICE_QTY', 0) or 0
            key = f'销售团队 {admin_unit_name} {employee_name} {shortcut}'
            
            if key not in item_code_summary:
                item_code_summary[key] = []
                item_code_values[key] = {}
                item_code_quantities[key] = {}
                
            # 如果该产品编码已存在，则累加金额和数量
            if item_name in item_code_values[key]:
                item_code_values[key][item_name] += amount
                item_code_quantities[key][item_name] += price_qty
            else:
                item_code_values[key][item_name] = amount
                item_code_quantities[key][item_name] = price_qty
        
        # 将汇总后的产品编码数据添加到结果中
        for shortcut_key, item_dict in item_code_values.items():
            for item_name, item_value in item_dict.items():
                item_code_summary[shortcut_key].append({
                    'name': item_name,
                    'value': item_value,
                    'quantity': item_code_quantities[shortcut_key][item_name],
                    'group_id': shortcut_key
                })

        # 构建完整的ECharts数据结构
        all_level_data = {
            '销售团队': list(department_summary.values())
        }
        all_level_data.update(employee_summary)
        all_level_data.update(shortcut_summary)
        all_level_data.update(item_code_summary)

        return all_level_data
    
    @staticmethod
    def process_percentage_data_for_echarts(data: List) -> Dict:
        """
        处理销售完成率数据，生成适用于ECharts的数据结构
        第一层展现销售团队的完成率，第二层展现团队下业务员的完成率
        
        参数:
        - data: 包含ADMIN_UNIT_NAME, EMPLOYEE_NAME, PRICE_AMOUNT, FORECAST_AMOUNT的对象列表
        
        返回:
        - 适用于ECharts的数据结构
        """
        # 第一层：按销售团队汇总完成率
        team_summary = {}
        team_amounts = {}
        for item in data:
            admin_unit_name = getattr(item, 'ADMIN_UNIT_NAME', None) or getattr(item, 'admin_unit_name', '') or ''
            price_amount = getattr(item, 'PRICE_AMOUNT', None) or getattr(item, 'price_amount', 0) or 0
            forecast_amount = getattr(item, 'FORECAST_AMOUNT', None) or getattr(item, 'forecast_amount', 0) or 0
            if admin_unit_name not in team_amounts:
                team_amounts[admin_unit_name] = {'price_sum': 0, 'forecast_sum': 0}
            team_amounts[admin_unit_name]['price_sum'] += price_amount
            team_amounts[admin_unit_name]['forecast_sum'] += forecast_amount
        for team, sums in team_amounts.items():
            price_sum = sums['price_sum']
            forecast_sum = sums['forecast_sum']
            completion_rate = round((price_sum / forecast_sum) * 100, 2) if forecast_sum > 0 else 0
            team_summary[team] = {
                'name': team,
                'value': completion_rate,
                'actual': price_sum,
                'target': forecast_sum,
                'group_id': '销售团队',
                'child_group_id': f'销售团队 {team}'
            }
        # 第二层：按业务员汇总完成率
        employee_summary = {}
        employee_amounts = {}
        for item in data:
            admin_unit_name = getattr(item, 'ADMIN_UNIT_NAME', None) or getattr(item, 'admin_unit_name', '') or ''
            employee_name = getattr(item, 'EMPLOYEE_NAME', None) or getattr(item, 'employee_name', '') or ''
            price_amount = getattr(item, 'PRICE_AMOUNT', None) or getattr(item, 'price_amount', 0) or 0
            forecast_amount = getattr(item, 'FORECAST_AMOUNT', None) or getattr(item, 'forecast_amount', 0) or 0
            key = f'销售团队 {admin_unit_name}'
            if key not in employee_summary:
                employee_summary[key] = []
                employee_amounts[key] = {}
            if employee_name not in employee_amounts[key]:
                employee_amounts[key][employee_name] = {'price_sum': 0, 'forecast_sum': 0}
            employee_amounts[key][employee_name]['price_sum'] += price_amount
            employee_amounts[key][employee_name]['forecast_sum'] += forecast_amount
        for team_key, emp_dict in employee_amounts.items():
            for emp_name, sums in emp_dict.items():
                price_sum = sums['price_sum']
                forecast_sum = sums['forecast_sum']
                completion_rate = round((price_sum / forecast_sum) * 100, 2) if forecast_sum > 0 else 0
                employee_summary[team_key].append({
                    'name': emp_name,
                    'value': completion_rate,
                    'actual': price_sum,
                    'target': forecast_sum,
                    'group_id': team_key,
                    'child_group_id': f'{team_key} {emp_name}'
                })
        # 构建完整的ECharts数据结构
        all_level_data = {
            '销售团队': list(team_summary.values())
        }
        all_level_data.update(employee_summary)
        return all_level_data








