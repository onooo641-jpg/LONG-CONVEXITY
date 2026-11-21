// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Aave v3 liquidation executor (candidate #100). Flash-loans the debt asset, liquidates, swaps the
// seized collateral back to the debt asset on Uniswap v3 (SwapRouter02) and reverts unless
// profit >= minProfit. SIMULATE-ONLY: only ever run on local forks in CI; never deployed, no funded key.

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
}

interface IPool {
    function flashLoanSimple(address receiver, address asset, uint256 amount, bytes calldata params, uint16 ref) external;
    function liquidationCall(address collateral, address debt, address user, uint256 debtToCover, bool receiveAToken) external;
}

interface ISwapRouter02 {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    struct ExactInputParams {
        bytes path;
        address recipient;
        uint256 amountIn;
        uint256 amountOutMinimum;
    }

    function exactInputSingle(ExactInputSingleParams calldata p) external payable returns (uint256);
    function exactInput(ExactInputParams calldata p) external payable returns (uint256);
}

contract LiqExecutor {
    address public immutable owner;
    IPool public immutable pool;
    ISwapRouter02 public immutable router;

    struct Params {
        address collateral;
        address debt;
        address user;
        uint256 debtToCover;
        uint24 fee;        // collateral -> (via or debt)
        address via;       // address(0) = direct pair
        uint24 fee2;       // via -> debt
        uint256 minProfit; // in debt-asset units
    }

    constructor(address pool_, address router_) {
        owner = msg.sender;
        pool = IPool(pool_);
        router = ISwapRouter02(router_);
    }

    function liquidate(Params calldata p) external {
        require(msg.sender == owner, "owner");
        pool.flashLoanSimple(address(this), p.debt, p.debtToCover, abi.encode(p), 0);
    }

    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params)
        external
        returns (bool)
    {
        require(msg.sender == address(pool) && initiator == address(this), "caller");
        Params memory p = abi.decode(params, (Params));
        require(asset == p.debt && amount == p.debtToCover, "params");

        _approve(p.debt, address(pool), amount);
        pool.liquidationCall(p.collateral, p.debt, p.user, amount, false);

        uint256 owed = amount + premium;
        if (p.collateral != p.debt) {
            uint256 collBal = IERC20(p.collateral).balanceOf(address(this));
            require(collBal > 0, "no collateral");
            uint256 have = IERC20(p.debt).balanceOf(address(this));
            uint256 minOut = owed + p.minProfit > have ? owed + p.minProfit - have : 0;
            _approve(p.collateral, address(router), collBal);
            if (p.via == address(0)) {
                router.exactInputSingle(
                    ISwapRouter02.ExactInputSingleParams(p.collateral, p.debt, p.fee, address(this), collBal, minOut, 0)
                );
            } else {
                router.exactInput(
                    ISwapRouter02.ExactInputParams(
                        abi.encodePacked(p.collateral, p.fee, p.via, p.fee2, p.debt), address(this), collBal, minOut
                    )
                );
            }
        }
        require(IERC20(p.debt).balanceOf(address(this)) >= owed + p.minProfit, "unprofitable");
        _approve(p.debt, address(pool), owed);
        return true;
    }

    function sweep(address token) external {
        require(msg.sender == owner, "owner");
        IERC20(token).transfer(owner, IERC20(token).balanceOf(address(this)));
    }

    // USDT-style tokens need approve(0) first and return no value
    function _approve(address token, address spender, uint256 amt) internal {
        (bool ok0,) = token.call(abi.encodeWithSelector(IERC20.approve.selector, spender, 0));
        ok0;
        (bool ok, bytes memory ret) = token.call(abi.encodeWithSelector(IERC20.approve.selector, spender, amt));
        require(ok && (ret.length == 0 || abi.decode(ret, (bool))), "approve");
    }
}
