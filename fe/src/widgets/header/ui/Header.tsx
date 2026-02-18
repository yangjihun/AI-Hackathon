import { Link, useNavigate } from "react-router-dom";
import { getCurrentUser, logout, isAuthenticated } from "../../../shared/lib/auth";
import { getCurrentPlan, setCurrentPlan as savePlan, PLANS, formatPrice, type PlanType } from "../../../shared/lib/subscription";
import { PlanModal } from "./PlanModal";
import { useState, useEffect } from "react";

export function Header() {
  const [user, setUser] = useState(getCurrentUser());
  const [showMenu, setShowMenu] = useState(false);
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [currentPlan, setCurrentPlan] = useState<PlanType>(getCurrentPlan());
  const navigate = useNavigate();

  useEffect(() => {
    // 인증 상태 변경 감지
    const checkAuth = () => {
      setUser(getCurrentUser());
      setCurrentPlan(getCurrentPlan());
    };
    window.addEventListener("storage", checkAuth);
    checkAuth();
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  const handleLogout = () => {
    logout();
    setUser(null);
    setShowMenu(false);
    navigate("/login");
  };

  const handlePlanChange = (planId: PlanType) => {
    setCurrentPlan(planId); // 상태 업데이트
    savePlan(planId); // localStorage에 저장
    setShowPlanModal(false);
    // 실제로는 결제 프로세스 진행
    alert(`${PLANS[planId].name} 요금제로 변경되었습니다! (데모)`);
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <Link to="/browse" className="header-logo">
          NetPlus
        </Link>
      </div>
      <div className="header-right">
        {isAuthenticated() && user && (
          <button
            className="header-plan-btn"
            onClick={() => setShowPlanModal(true)}
            aria-label="요금제"
          >
            <span className="header-plan-badge">{PLANS[currentPlan].name}</span>
            <span className="header-plan-text">요금제</span>
          </button>
        )}
        {isAuthenticated() && user ? (
          <div className="header-user-menu">
            <button
              className="header-profile-btn"
              onClick={() => setShowMenu(!showMenu)}
              aria-label="프로필 메뉴"
            >
              <span className="header-profile-icon">👤</span>
              <span className="header-profile-name">{user.name}</span>
            </button>
            {showMenu && (
              <div className="header-dropdown">
                <div className="header-dropdown-item">
                  <span className="header-dropdown-email">{user.email}</span>
                </div>
                <button
                  className="header-dropdown-item header-dropdown-button"
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link to="/login" className="header-login-btn">
            로그인
          </Link>
        )}
        <button className="header-search-btn" aria-label="검색">
          🔍
        </button>
      </div>

      {showPlanModal && (
        <PlanModal
          currentPlan={currentPlan}
          onClose={() => setShowPlanModal(false)}
          onPlanChange={handlePlanChange}
        />
      )}
    </header>
  );
}

