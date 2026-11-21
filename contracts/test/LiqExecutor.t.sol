// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {LiqExecutor, IPool, IERC20} from "../src/LiqExecutor.sol";

interface Vm {
    function createSelectFork(string calldata url) external returns (uint256);
    function envString(string calldata) external view returns (string memory);
    function envAddress(string calldata) external view returns (address);
    function envUint(string calldata, string calldata) external view returns (uint256[] memory);
    function deal(address, uint256) external;
    function prank(address) external;
    function startPrank(address) external;
    function stopPrank() external;
    function mockCall(address, bytes calldata, bytes calldata) external;
    function load(address, bytes32) external view returns (bytes32);
    function store(address, bytes32, bytes32) external;
    function envOr(string calldata, string calldata) external view returns (string memory);
    function envUint(string calldata) external view returns (uint256);
}

interface IProvider {
    function getPriceOracle() external view returns (address);
}

interface IOracle {
    function getAssetPrice(address) external view returns (uint256);
}

interface IPoolFull is IPool {
    function ADDRESSES_PROVIDER() external view returns (address);
    function supply(address asset, uint256 amount, address onBehalfOf, uint16 ref) external;
    function borrow(address asset, uint256 amount, uint256 mode, uint16 ref, address onBehalfOf) external;
    function getUserAccountData(address user)
        external
        view
        returns (uint256 coll, uint256 debt, uint256 avail, uint256 lt, uint256 ltv, uint256 hf);
}

interface IDec {
    function decimals() external view returns (uint8);
}

interface IWrapped {
    function deposit() external payable;
}

// Run: RPC_URL=... POOL=... COLL=<wrapped native> DEBT=<USDC> ROUTER=... FEES=500,3000 forge test --root contracts -vv
contract LiqExecutorForkTest {
    Vm constant vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    IPoolFull pool;
    address coll;
    address debt;
    address router;
    uint256[] fees;
    address borrower = address(0xB0B0B0);
    address oracle;
    LiqExecutor ex;
    uint256 toCover;

    function _hex(bytes memory b) internal pure returns (string memory) {
        bytes16 H = "0123456789abcdef";
        uint256 n = b.length > 68 ? 68 : b.length;
        bytes memory o = new bytes(2 * n);
        for (uint256 i = 0; i < n; i++) {
            o[2 * i] = H[uint8(b[i]) >> 4];
            o[2 * i + 1] = H[uint8(b[i]) & 0x0f];
        }
        return string(o);
    }

    // set a plain ERC20 balance by finding its balances mapping slot (no forge-std needed)
    function _dealToken(address token, address to, uint256 amt) internal {
        for (uint256 k = 0; k < 150; k++) {
            bytes32 slot = keccak256(abi.encode(to, k));
            bytes32 old = vm.load(token, slot);
            vm.store(token, slot, bytes32(amt));
            if (IERC20(token).balanceOf(to) == amt) return;
            vm.store(token, slot, old);
        }
        revert("balance slot not found");
    }

    function _u(uint256 v) internal pure returns (string memory) {
        if (v == 0) return "0";
        uint256 t = v;
        uint256 d;
        while (t != 0) { d++; t /= 10; }
        bytes memory b = new bytes(d);
        while (v != 0) { d--; b[d] = bytes1(uint8(48 + v % 10)); v /= 10; }
        return string(b);
    }

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC_URL"));
        pool = IPoolFull(vm.envAddress("POOL"));
        coll = vm.envAddress("COLL");
        debt = vm.envAddress("DEBT");
        router = vm.envAddress("ROUTER");
        fees = vm.envUint("FEES", ",");
        oracle = IProvider(pool.ADDRESSES_PROVIDER()).getPriceOracle();
        require(router.code.length > 0, "router has no code");
        require(address(pool).code.length > 0, "pool has no code");

        // position sized in USD (Aave v3.3+ rejects partial liquidations that leave dust, so tiny positions are not representative)
        uint256 amt = vm.envUint("AMT_USD") * 1e8 * (10 ** uint256(IDec(coll).decimals())) / IOracle(oracle).getAssetPrice(coll);
        // collateral is the chain's wrapped native token (WETH9-style): fund the borrower with native token and wrap it
        bool slotMode = keccak256(bytes(vm.envOr("FUND", "wrap"))) == keccak256(bytes("slot"));
        if (slotMode) {
            _dealToken(coll, borrower, amt);
            vm.startPrank(borrower);
        } else {
            vm.deal(borrower, amt);
            vm.startPrank(borrower);
            try IWrapped(coll).deposit{value: amt}() {} catch (bytes memory r) { revert(string.concat("deposit: ", _hex(r))); }
        }
        IERC20(coll).approve(address(pool), type(uint256).max);
        try pool.supply(coll, amt, borrower, 0) {} catch (bytes memory r) { revert(string.concat("supply: ", _hex(r))); }
        (,, uint256 avail,,,) = pool.getUserAccountData(borrower);
        // avail is in 1e8 USD; borrow 99% of it in debt-asset units at the oracle price
        uint256 pd = IOracle(oracle).getAssetPrice(debt);
        uint256 dd = 10 ** uint256(IDec(debt).decimals());
        uint256 borrowAmt = (avail * 99 / 100) * dd / pd;
        try pool.borrow(debt, borrowAmt, 2, 0, borrower) {} catch (bytes memory r) { revert(string.concat("borrow: ", _hex(r))); }
        vm.stopPrank();
        toCover = borrowAmt * 1001 / 1000; // more than the debt: Aave caps it, avoids a dust remainder
        ex = new LiqExecutor(address(pool), router);
    }

    function _mockCollateralDown() internal {
        uint256 p = IOracle(oracle).getAssetPrice(coll);
        vm.mockCall(oracle, abi.encodeWithSelector(IOracle.getAssetPrice.selector, coll), abi.encode(p * 85 / 100));
    }

    function _params(uint24 fee, uint256 minProfit) internal view returns (LiqExecutor.Params memory) {
        return LiqExecutor.Params(coll, debt, borrower, toCover, fee, address(0), 0, minProfit);
    }

    // (i) + (iii): unhealthy position is liquidated, flash loan repaid (else Aave reverts), profit left in executor
    function test_profitable_liquidation_repays_flash_loan() public {
        _mockCollateralDown();
        (,,,,, uint256 hfBefore) = pool.getUserAccountData(borrower);
        require(hfBefore < 1e18, "position not unhealthy");
        bool done;
        string memory why;
        for (uint256 i = 0; i < fees.length && !done; i++) {
            try ex.liquidate(_params(uint24(fees[i]), 1)) {
                done = true;
            } catch (bytes memory r) {
                why = string.concat(why, " fee", _u(fees[i]), ":", _hex(r));
            }
        }
        if (!done) revert(string.concat("no fee tier worked:", why));
        require(IERC20(debt).balanceOf(address(ex)) > 0, "no profit");
        require(IERC20(coll).balanceOf(address(ex)) <= 1e3 || coll == debt, "collateral left behind");
        (,,,,, uint256 hfAfter) = pool.getUserAccountData(borrower);
        require(hfAfter > hfBefore, "debt not reduced");
    }

    // (ii): reverts when profit is below minProfit
    function test_reverts_when_below_min_profit() public {
        _mockCollateralDown();
        bool ok;
        for (uint256 i = 0; i < fees.length; i++) {
            try ex.liquidate(_params(uint24(fees[i]), type(uint128).max)) {
                ok = true;
            } catch {}
        }
        require(!ok, "should revert below min profit");
        require(IERC20(debt).balanceOf(address(ex)) == 0, "funds moved");
    }

    // (iv): healthy position cannot be liquidated; unusable route reverts
    function test_reverts_on_healthy_position() public {
        bool ok;
        for (uint256 i = 0; i < fees.length; i++) {
            try ex.liquidate(_params(uint24(fees[i]), 1)) {
                ok = true;
            } catch {}
        }
        require(!ok, "healthy position was liquidated");
    }

    function test_reverts_on_unusable_route() public {
        _mockCollateralDown();
        try ex.liquidate(_params(777, 1)) {
            revert("bad route did not revert");
        } catch {}
    }
}
