import { Settings2 } from "lucide-react";

export function DataTableColumnToggle({ table }) {
  return (
    <div className="flex items-center gap-2 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg flex-wrap">
      <div className="flex items-center gap-2">
        <Settings2 className="w-4 h-4 text-gray-600 dark:text-gray-400" />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">显示列：</span>
      </div>
      <div className="flex items-center gap-3 flex-wrap">
        {table
          .getAllColumns()
          .filter(column => column.getCanHide())
          .map(column => {
            const displayName = column.columnDef.meta?.displayName || column.id;
            return (
              <label key={column.id} className="flex items-center gap-1.5 text-sm cursor-pointer hover:text-blue-600">
                <input
                  type="checkbox"
                  checked={column.getIsVisible()}
                  onChange={e => column.toggleVisibility(e.target.checked)}
                  className="rounded cursor-pointer"
                />
                <span>{displayName}</span>
              </label>
            );
          })}
      </div>
    </div>
  );
}
