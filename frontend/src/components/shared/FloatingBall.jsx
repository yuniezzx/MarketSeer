import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { BookOpen, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { getExplanationForRoute } from "@/lib/pageExplanations";

/**
 * 悬浮球组件 - 显示当前页面的字段解释
 */
function FloatingBall() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [explanation, setExplanation] = useState(null);

  // 监听路由变化，更新解释内容
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const content = getExplanationForRoute(location.pathname, searchParams);
    setExplanation(content);

    // 路由变化时关闭弹窗
    setIsOpen(false);
  }, [location.pathname, location.search]);

  // 如果当前页面没有配置解释内容，不显示悬浮球
  if (!explanation) {
    return null;
  }

  return (
    <>
      {/* 悬浮球按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
        aria-label="字段解释"
      >
        {isOpen ? <X className="w-6 h-6" /> : <BookOpen className="w-6 h-6" />}
      </button>

      {/* 解释内容卡片 */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 max-h-[600px] animate-in fade-in slide-in-from-bottom-4 duration-300">
          <Card className="p-4 shadow-2xl overflow-y-auto max-h-[600px]">
            {/* 标题 */}
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-600" />
                {explanation.title}
              </h3>
            </div>

            {/* 字段列表 */}
            <div className="space-y-4">
              {explanation.fields.map((field, index) => (
                <div
                  key={index}
                  className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
                >
                  <div className="font-medium text-gray-900 dark:text-gray-100 mb-1">{field.name}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{field.description}</div>
                </div>
              ))}
            </div>

            {/* 底部提示 */}
            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center">点击右下角按钮关闭</p>
            </div>
          </Card>
        </div>
      )}

      {/* 遮罩层（点击关闭） */}
      {isOpen && (
        <div className="fixed inset-0 z-40 bg-black/20 animate-in fade-in duration-300" onClick={() => setIsOpen(false)} />
      )}
    </>
  );
}

export default FloatingBall;
